import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .calendar_repository import CalendarRepo
from .calendar_models import Calendar
from src.database.routines.routine_models import Routine
from src.database.routines.routine_service import RoutineService
from src.api.utils.caldav_client import CalDAVClient
from src.database.base.exceptions import ValidationError

class CalendarService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = CalendarRepo(session)

    def discover_remote_calendars(self, client: CalDAVClient) -> List[Dict]:
        """Test credentials and return list of remote calendars without saving"""
        if not client.connect():
            raise ValidationError("Failed to connect to CalDAV server.")
        
        calendars = client.get_calendars()
        return [{"name": c.name, "uid": c.uid, "url": c.url, "color": c.color} for c in calendars]

    def sync_calendar(self, user_id: int, remote_uid: str, client: CalDAVClient, user_timezone: str) -> Dict:
        """
        Sync a single remote calendar:
        1. Ensure local Calendar record exists.
        2. Fetch remote events.
        3. Create/Update Routines (preventing duplicates).

        Args:
            user_id: ID of the user
            remote_uid: UID of the remote calendar
            client: CalDAV client instance
            user_timezone: User's IANA timezone string (e.g., 'America/Chicago')
        """
        if not client.connect():
            raise ValidationError("Failed to connect to CalDAV server.")

        # 1. Find the specific remote calendar
        remote_cals = client.get_calendars()
        remote_info = next((c for c in remote_cals if c.uid == remote_uid), None)
        if not remote_info:
            raise ValidationError(f"Remote calendar {remote_uid} not found.")

        # 2. Ensure local Calendar record exists
        local_cal = self.session.query(Calendar).filter_by(
            user_id=user_id, external_uid=remote_uid
        ).first()

        if not local_cal:
            local_cal = self.repo.create(
                user_id=user_id,
                name=remote_info.name,
                color=remote_info.color,
                timezone=user_timezone,
                external_uid=remote_info.uid,
                external_source='caldav'
            )
        else:
            # Update timezone if calendar already exists
            local_cal.timezone = user_timezone
            self.session.commit()

        # 3. Sync events as Routines
        events = client.get_events(remote_info.url)
        routine_service = RoutineService(self.session)
        created_count = 0

        for event in events:
            if not event.rrule:
                continue

            # If event.start is a datetime, we can get the weekday
            if hasattr(event.start, 'weekday'):
                weekday = event.start.weekday()
                weekday_names = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

                # If RRULE is weekly but doesn't specify BYDAY, add it
                if 'FREQ=WEEKLY' in event.rrule and 'BYDAY' not in event.rrule:
                    event.rrule = f"{event.rrule};BYDAY={weekday_names[weekday]}"
                    logging.debug(f"  Added weekday to RRULE: {event.rrule}")

            # Duplicate Check: Name + Source + RRule
            existing = self.session.query(Routine).filter_by(
                user_id=user_id,
                title=event.summary,
                external_source='caldav',
                rrule=event.rrule
            ).first()

            if not existing:
                # Extract time components from the event's start/end times (store as-is, no conversion)
                start_time = event.start.time()
                end_time = event.end.time() if event.end else None

                routine_service.create_routine(user_id, {
                    "title": event.summary,
                    "description": event.description,
                    "rrule": event.rrule,
                    "start_time": start_time.strftime('%H:%M'),
                    "end_time": end_time.strftime('%H:%M') if end_time else None,
                    "timezone": user_timezone,
                    "calendar_id": local_cal.id,
                    "calendar_color": local_cal.color,
                    "external_uid": event.uid,
                    "external_source": 'caldav'
                })
                created_count += 1

        return {"calendar_id": local_cal.id, "created_routines": created_count}

    def create_calendar(self, user_id: int, data: Dict[str, Any], timezone: str = 'UTC') -> Calendar:
        """Manually create a local calendar record
        
        Args:
            user_id: ID of the user
            data: Dictionary containing 'name' and optional 'color'
            timezone: IANA timezone string (defaults to 'UTC')
        """
        if not data.get('name'):
            raise ValidationError("Calendar name is required.")
        
        return self.repo.create(
            user_id=user_id,
            name=data['name'],
            color=data.get('color', '#767676'),
            timezone=timezone
        )

    def list_calendars(self, user_id: int, include_inactive: bool = False) -> List[Calendar]:
        """
        List calendars for a user.

        Args:
            user_id: ID of the user
            include_inactive: If False (default), only returns active calendars

        Returns:
            List of calendars
        """
        calendars = self.repo.list_for_user(user_id)
        if not include_inactive:
            calendars = [c for c in calendars if c.active]
        return calendars

    def get_calendar(self, user_id: int, calendar_id: int) -> Calendar:
        """Get a specific calendar, ensuring user ownership"""
        return self.repo.get(user_id, calendar_id)

    def update_calendar(self, user_id: int, calendar_id: int, data: Dict[str, Any]) -> Calendar:
        """
        Update a calendar's properties.
        Only allows updating: name, color
        Prevents updating: external_uid, external_source, active

        Args:
            user_id: ID of the user who owns the calendar
            calendar_id: ID of the calendar to update
            data: Dictionary of fields to update

        Returns:
            Updated calendar
        """
        self.repo.get(user_id, calendar_id)

        # Whitelist of updatable fields (removed 'active')
        updatable = ['name', 'color']
        update_data = {k: v for k, v in data.items() if k in updatable}

        if 'name' in update_data and not update_data['name']:
            raise ValidationError("Calendar name cannot be empty.")

        # If color is being updated, cascade the change to routines and sessions
        if 'color' in update_data:
            updated_calendar = self.repo.update(user_id, calendar_id, **update_data)
            self.cascade_color_change(user_id, calendar_id, update_data['color'])
            return updated_calendar

        return self.repo.update(user_id, calendar_id, **update_data)

    def cascade_color_change(self, user_id: int, calendar_id: int, new_color: str) -> int:
        """
        Cascade a calendar color change to all associated routines and their sessions.

        Args:
            user_id: ID of the user who owns the calendar
            calendar_id: ID of the calendar whose color changed
            new_color: The new color value (hex format, e.g., '#1a73e8')

        Returns:
            Number of routines (and their sessions) updated
        """
        calendar = self.repo.get(user_id, calendar_id)

        routine_service = RoutineService(self.session)
        updated_count = 0

        # Update all routines associated with this calendar
        for routine in calendar.routines:
            # Update the routine's calendar_color
            self.session.query(Routine).filter_by(id=routine.id).update(
                {'calendar_color': new_color}
            )

            # Cascade color change to all sessions of this routine
            routine_service._cascade_to_sessions(
                routine_id=routine.id,
                user_id=user_id,
                update_data={'calendar_color': new_color},
                scope='all',
                cascade_fields={'calendar_color'}
            )

            updated_count += 1

        self.session.commit()
        logging.info(f"Cascaded color change to {updated_count} routines and their sessions for calendar {calendar_id}")
        return updated_count

    def activate_calendar(self, user_id: int, calendar_id: int, cascade: bool = False) -> Calendar:
        """
        Activate a calendar.

        Args:
            user_id: ID of the user who owns the calendar
            calendar_id: ID of the calendar to activate
            cascade: If True, also activate all routines in this calendar (default: False)

        Returns:
            Updated calendar
        """
        self.repo.get(user_id, calendar_id)

        # Activate the calendar
        calendar = self.repo.update(user_id, calendar_id, active=True)

        # Cascade activation to routines if requested
        if cascade:
            for routine in calendar.routines:
                routine.active = True
            self.session.commit()
            logging.info(f"Cascaded activation to {len(calendar.routines)} routines for calendar {calendar_id}")

        return calendar

    def deactivate_calendar(self, user_id: int, calendar_id: int, cascade: bool = True) -> Calendar:
        """
        Deactivate a calendar.

        Args:
            user_id: ID of the user who owns the calendar
            calendar_id: ID of the calendar to deactivate
            cascade: If True, also deactivate all routines in this calendar (default: True)

        Returns:
            Updated calendar
        """
        self.repo.get(user_id, calendar_id)

        # Deactivate the calendar
        calendar = self.repo.update(user_id, calendar_id, active=False)

        # Cascade deactivation to routines if requested
        if cascade:
            for routine in calendar.routines:
                routine.active = False
            self.session.commit()
            logging.info(f"Cascaded deactivation to {len(calendar.routines)} routines for calendar {calendar_id}")

        return calendar


    def delete_calendar(self, user_id: int, calendar_id: int) -> None:
        """
        Delete a calendar and all its associated routines and sessions.
        Sessions are automatically deleted via cascade in Routine model.

        Args:
            user_id: ID of the user who owns the calendar
            calendar_id: ID of the calendar to delete
        """
        self.repo.get(user_id, calendar_id)

        self.repo.delete(user_id, calendar_id)