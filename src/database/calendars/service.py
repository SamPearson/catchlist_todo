from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .repository import CalendarRepo
from .models import Calendar
from src.database.routines.models import Routine
from src.database.routines.service import RoutineService
from src.config.caldav_client import CalDAVClient
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

    def sync_calendar(self, user_id: int, remote_uid: str, client: CalDAVClient) -> Dict:
        """
        Sync a single remote calendar:
        1. Ensure local Calendar record exists.
        2. Fetch remote events.
        3. Create/Update Routines (preventing duplicates).
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
                external_uid=remote_info.uid,
                external_source='caldav'
            )

        # 3. Sync events as Routines
        events = client.get_events(remote_info.url)
        routine_service = RoutineService(self.session)
        created_count = 0
        
        for event in events:
            if not event.rrule:
                continue

            # Duplicate Check: Name + Source + RRule
            existing = self.session.query(Routine).filter_by(
                user_id=user_id,
                title=event.summary,
                external_source='caldav',
                rrule=event.rrule
            ).first()

            if not existing:
                routine_service.create_routine(user_id, {
                    "title": event.summary,
                    "description": event.description,
                    "rrule": event.rrule,
                    "calendar_id": local_cal.id,
                    "external_uid": event.uid,
                    "external_source": 'caldav',
                    "timezone": event.timezone
                })
                created_count += 1
        
        return {"calendar_id": local_cal.id, "created_routines": created_count}

    def create_calendar(self, user_id: int, data: Dict[str, Any]) -> Calendar:
        """Manually create a local calendar record"""
        if not data.get('name'):
            raise ValidationError("Calendar name is required.")
            
        return self.repo.create(
            user_id=user_id,
            name=data['name'],
            color=data.get('color', '#767676'),
            external_uid=data.get('external_uid'),
            external_source=data.get('external_source', 'manual')
        )

    def list_calendars(self, user_id: int) -> List[Calendar]:
        return self.repo.list_for_user(user_id)