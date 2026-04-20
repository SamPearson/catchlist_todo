from typing import List, Dict, Any, Optional
from datetime import datetime, time
from sqlalchemy.orm import Session
from .routine_models import Routine
from .repository import RoutineRepo
from src.database.base.exceptions import ValidationError
from src.database.base.exceptions import EntityNotFoundError
from src.database.sessions.session_models import RoutineSession
from src.database.sessions.session_repository import SessionRepo
from src.database.timeframes.timeframe_service import TimeframeService
from src.database.commitments.commitment_service import CommitmentService
from src.utils.timezone import compute_timeframe_bounds, utc_to_local_date
from dateutil.rrule import rrulestr
import logging



class RoutineValidationError(ValidationError):
    pass


class RoutineService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = RoutineRepo(session)
        self.session_repo = SessionRepo(session)
        self.timeframe_service = TimeframeService(session)
        self.commitment_service = CommitmentService(session)

    def get_routine(self, routine_id: int, user_id: int) -> Optional[Routine]:
        return self.repo.get(routine_id, user_id)

    def list_routines(self, user_id: int, active_only: bool = True) -> List[Routine]:
        filters = {}
        if active_only:
            filters['active'] = True
        return self.repo.list_for_user(user_id, **filters)

    def create_routine(self, user_id: int, data: Dict[str, Any]) -> Routine:
        from ..calendars.calendar_service import CalendarService #importing here to avoid cicular import
        self.calendar_service = CalendarService(self.session)

        if not data.get('title'):
            raise RoutineValidationError("Title is required for routines")

        if data.get('title').strip() == '':
            raise RoutineValidationError("Title cannot be empty")

        if len(data.get('title', '')) > 200:
            raise RoutineValidationError("Title cannot exceed 200 characters")

        if data.get('rrule'):
            try:
                rrulestr(data['rrule'])
            except ValueError as e:
                raise RoutineValidationError(f"Invalid rrule: {e}")


        # Convert time strings to time objects
        start_time = None
        end_time = None
        
        if 'start_time' in data and data['start_time']:
            try:
                # Accept HH:MM format
                hours, minutes = map(int, data['start_time'].split(':'))
                start_time = time(hours, minutes)
            except ValueError:
                raise RoutineValidationError("start_time must be in HH:MM format")

        if 'end_time' in data and data['end_time']:
            try:
                hours, minutes = map(int, data['end_time'].split(':'))
                end_time = time(hours, minutes)
            except ValueError:
                raise RoutineValidationError("end_time must be in HH:MM format")

        calendar_id = data.get('calendar_id')
        if calendar_id and not self.calendar_service.get_calendar(calendar_id, user_id):
            raise RoutineValidationError( f"Calendar {calendar_id} not found.")

        return self.repo.create(
            user_id = user_id,
            title = data['title'],
            description = data.get('description'),
            rrule = data.get('rrule'),
            start_time = start_time,
            end_time = end_time,
            active = data.get('active', True),
            external_uid = data.get('external_uid'),
            external_source = data.get('external_source'),
            external_source_name = data.get('external_source_name'),
            calendar_id = calendar_id
        )


    def get_future_sessions(self, routine_id: int, user_id: int,
                            reference_time: Optional[datetime] = None) -> List[RoutineSession]:
        """
        Get all future sessions for a routine (excluding passed sessions).

        Args:
            routine_id: ID of the routine
            user_id: ID of the user who owns the routine
            reference_time: Time to compare against (default: now in UTC)

        Returns:
            List of sessions with start_time >= reference_time, ordered by start_time
        """
        if reference_time is None:
            reference_time = datetime.utcnow()

        routine = self.get_routine(routine_id, user_id)
        if not routine:
            return []

        return [s for s in routine.sessions if s.start_time >= reference_time]


    def get_past_sessions(self, routine_id: int, user_id: int,
                          reference_time: Optional[datetime] = None) -> List[RoutineSession]:
        """
        Get all past sessions for a routine (excluding future sessions).

        Args:
            routine_id: ID of the routine
            user_id: ID of the user who owns the routine
            reference_time: Time to compare against (default: now in UTC)

        Returns:
            List of sessions with start_time < reference_time, ordered by start_time (newest first)
        """
        if reference_time is None:
            reference_time = datetime.utcnow()

        routine = self.get_routine(routine_id, user_id)
        if not routine:
            return []

        return sorted(
            [s for s in routine.sessions if s.start_time < reference_time],
            key=lambda s: s.start_time,
            reverse=True
        )


    def get_incomplete_sessions(self, routine_id: int, user_id: int,
                                reference_time: Optional[datetime] = None) -> List[RoutineSession]:
        """
        Get all incomplete (not completed/skipped/cancelled) future sessions for a routine.

        Args:
            routine_id: ID of the routine
            user_id: ID of the user who owns the routine
            reference_time: Time to compare against (default: now in UTC)

        Returns:
            List of future sessions with status='scheduled'
        """
        future_sessions = self.get_future_sessions(routine_id, user_id, reference_time)
        return [s for s in future_sessions if s.status == 'scheduled']


    def delete_future_sessions(self, routine_id: int, user_id: int,
                               incomplete_only: bool = True,
                               reference_time: Optional[datetime] = None) -> int:
        """
        Delete future sessions for a routine.

        Args:
            routine_id: ID of the routine
            user_id: ID of the user who owns the routine
            incomplete_only: If True, only delete 'scheduled' sessions; if False, delete all
            reference_time: Time to compare against (default: now in UTC)

        Returns:
            Number of sessions deleted
        """
        if incomplete_only:
            sessions_to_delete = self.get_incomplete_sessions(routine_id, user_id, reference_time)
        else:
            sessions_to_delete = self.get_future_sessions(routine_id, user_id, reference_time)

        deleted_count = 0
        for session in sessions_to_delete:
            if self.session_repo.delete(session):
                deleted_count += 1

        logging.info(f"Deleted {deleted_count} future sessions for routine {routine_id}")
        return deleted_count


    def cascade_routine_name_to_sessions(self, routine_id: int, user_id: int,
                                         new_name: str,
                                         scope: str = 'all') -> int:
        """
        Update routine_name on associated sessions.

        Args:
            routine_id: ID of the routine
            user_id: ID of the user who owns the routine
            new_name: The new routine name
            scope: 'all' = all sessions, 'future' = only future sessions, 'past' = only past sessions

        Returns:
            Number of sessions updated
        """
        routine = self.get_routine(routine_id, user_id)
        if not routine:
            return 0

        if scope == 'future':
            sessions_to_update = self.get_future_sessions(routine_id, user_id)
        elif scope == 'past':
            sessions_to_update = self.get_past_sessions(routine_id, user_id)
        else:  # 'all'
            sessions_to_update = routine.sessions

        updated_count = 0
        for session in sessions_to_update:
            self.session_repo.update(session, routine_name=new_name)
            updated_count += 1

        logging.info(f"Updated routine_name for {updated_count} sessions (scope: {scope})")
        return updated_count

    def update_routine(self, routine_id: int, user_id: int, data: Dict[str, Any],
                       cascade_future: bool = False, cascade_past: bool = False) -> Optional[Routine]:
        """
        Update routine properties with optional cascade to sessions.

        Cascade behavior:
        - title: Updates routine_name in sessions
        - start_time/end_time: Updates start_time/end_time in sessions
        - Other fields (description, rrule, active): No cascade

        Args:
            routine_id: ID of the routine
            user_id: ID of the user who owns the routine
            data: Dictionary of fields to update
            cascade_future: If True, cascade cascadeable fields to future sessions
            cascade_past: If True, cascade cascadeable fields to past sessions
        """
        routine = self.get_routine(routine_id, user_id)
        if not routine:
            raise EntityNotFoundError(f"Routine {routine_id} not found")

        # Standardize allowed update fields
        updatable = ['title', 'description', 'rrule', 'active', 'start_time', 'end_time']
        update_data = {k: v for k, v in data.items() if k in updatable}

        if data.get('rrule'):
            try:
                rrulestr(data['rrule'])
            except ValueError as e:
                raise RoutineValidationError(f"Invalid rrule: {e}")

        if 'title' in update_data and not update_data['title']:
            raise RoutineValidationError("Title cannot be empty")

        # Convert time strings to time objects
        if 'start_time' in update_data:
            try:
                hours, minutes = map(int, update_data['start_time'].split(':'))
                update_data['start_time'] = time(hours, minutes)
            except ValueError:
                raise RoutineValidationError("start_time must be in HH:MM format")

        if 'end_time' in update_data:
            try:
                hours, minutes = map(int, update_data['end_time'].split(':'))
                update_data['end_time'] = time(hours, minutes)
            except ValueError:
                raise RoutineValidationError("end_time must be in HH:MM format")

        # Determine which fields are cascadeable and being updated
        cascadeable_fields = {'title', 'start_time', 'end_time'}
        fields_to_cascade = set(update_data.keys()) & cascadeable_fields

        # Cascade changes to sessions if requested
        if fields_to_cascade:
            if cascade_future:
                self._cascade_to_sessions(routine_id, user_id, update_data, scope='future',
                                          cascade_fields=fields_to_cascade)
            if cascade_past:
                self._cascade_to_sessions(routine_id, user_id, update_data, scope='past',
                                          cascade_fields=fields_to_cascade)

        # Update the routine itself
        return self.repo.update(routine, **update_data)

    def _cascade_to_sessions(self, routine_id: int, user_id: int, update_data: Dict[str, Any],
                             scope: str = 'future', cascade_fields: Optional[set] = None) -> int:
        """
        Cascade routine updates to sessions.

        Args:
            routine_id: ID of the routine
            user_id: ID of the user
            update_data: Dictionary of fields being updated
            scope: 'future', 'past', or 'all'
            cascade_fields: Set of field names to cascade (title, start_time, end_time)

        Returns:
            Number of sessions updated
        """
        if cascade_fields is None:
            cascade_fields = {'title', 'start_time', 'end_time'}

        # Get sessions based on scope
        if scope == 'future':
            sessions_to_update = self.get_future_sessions(routine_id, user_id)
        elif scope == 'past':
            sessions_to_update = self.get_past_sessions(routine_id, user_id)
        else:  # 'all'
            routine = self.get_routine(routine_id, user_id)
            sessions_to_update = routine.sessions if routine else []

        updated_count = 0

        for session in sessions_to_update:
            session_update_data = {}

            # Map routine fields to session fields
            if 'title' in cascade_fields and 'title' in update_data:
                session_update_data['routine_name'] = update_data['title']

            # For start_time: combine routine's time with session's existing date
            if 'start_time' in cascade_fields and 'start_time' in update_data:
                new_time = update_data['start_time']  # This is a time object
                # Combine with the session's existing date
                new_start_datetime = datetime.combine(session.start_time.date(), new_time)
                session_update_data['start_time'] = new_start_datetime

            # For end_time: combine routine's time with session's existing date
            if 'end_time' in cascade_fields and 'end_time' in update_data:
                new_time = update_data['end_time']  # This is a time object
                # Combine with the session's existing date
                new_end_datetime = datetime.combine(session.end_time.date(), new_time)
                session_update_data['end_time'] = new_end_datetime

            if session_update_data:
                self.session_repo.update(session, **session_update_data)
                updated_count += 1

        logging.info(f"Cascaded updates to {updated_count} {scope} sessions for routine {routine_id}")
        return updated_count


    def delete_routine(self, routine_id: int, user_id: int) -> bool:
        """
        Delete a routine and all its associated sessions.
        Sessions will be automatically deleted due to cascade setting in relationship.

        Args:
            routine_id: ID of the routine to delete
            user_id: ID of the user who owns the routine

        Returns:
            bool: True if routine was found and deleted, False otherwise
        """
        routine = self.get_routine(routine_id, user_id)
        if not routine:
            raise EntityNotFoundError(f"Routine {routine_id} not found")


        return self.repo.delete(routine)