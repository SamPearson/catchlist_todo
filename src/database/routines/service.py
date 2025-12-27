from typing import List, Dict, Any, Optional
from datetime import datetime, time
from sqlalchemy.orm import Session
from .models import Routine
from .repository import RoutineRepo
from src.database.base.exceptions import ValidationError
from src.database.sessions.models import RoutineSession
from src.database.sessions.repository import SessionRepo
from dateutil.rrule import rrulestr
import logging


class RoutineValidationError(ValidationError):
    pass


class RoutineService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = RoutineRepo(session)
        self.session_repo = SessionRepo(session)

    def get_routine(self, routine_id: int, user_id: int) -> Optional[Routine]:
        return self.repo.get(routine_id, user_id)

    def list_routines(self, user_id: int, active_only: bool = True) -> List[Routine]:
        filters = {}
        if active_only:
            filters['active'] = True
        return self.repo.list_for_user(user_id, **filters)

    def create_routine(self, user_id: int, data: Dict[str, Any]) -> Routine:
        if not data.get('title'):
            raise RoutineValidationError("Title is required for routines")

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

        return self.repo.create(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            rrule=data.get('rrule'),
            start_time=start_time,
            end_time=end_time,
            active=data.get('active', True),
            external_uid=data.get('external_uid'),
            external_source=data.get('external_source', 'manual'),
            external_source_name=data.get('external_source_name'),
            calendar_id=data.get('calendar_id')
        )

    def update_routine(self, routine_id: int, user_id: int, data: Dict[str, Any]) -> Optional[Routine]:
        routine = self.get_routine(routine_id, user_id)
        if not routine:
            return None

        # Standardize allowed update fields
        updatable = ['title', 'description', 'rrule', 'active', 'start_time', 'end_time']
        update_data = {k: v for k, v in data.items() if k in updatable}

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

        return self.repo.update(routine, **update_data)

    def generate_sessions(self, user_id: int, routine_id: int, start_date: datetime,
                         end_date: datetime) -> List[RoutineSession]:
        """
        Generate sessions for a routine based on its recurrence rule within a date range.
        """
        routine = self.get_routine(routine_id, user_id)
        if not routine:
            raise RoutineValidationError(f"Routine with ID {routine_id} not found")

        if not routine.rrule:
            raise RoutineValidationError("Routine has no recurrence rule")

        if not routine.start_time:
            raise RoutineValidationError("Routine has no start time")

        # Create base datetime for rrule using start_date's date and routine's time
        base_dt = datetime.combine(start_date.date(), routine.start_time)
        
        # Create rule for generating occurrences
        rule = rrulestr(routine.rrule, dtstart=base_dt)

        try:
            # Generate occurrences within the specified range
            occurrences = rule.between(start_date, end_date, inc=True)
            
            # Create sessions for each occurrence
            created_sessions = []
            for occurrence_date in occurrences:
                # Combine occurrence date with routine times
                session_start = datetime.combine(occurrence_date.date(), routine.start_time)
                session_end = datetime.combine(occurrence_date.date(), routine.end_time)

                # Check if session already exists
                existing = self.session_repo.list_for_window(
                    user_id=user_id,
                    start=session_start,
                    end=session_start
                )

                if not existing:
                    session = self.session_repo.create(
                        user_id=user_id,
                        routine_id=routine_id,
                        start_time=session_start,
                        end_time=session_end,
                        notes='Auto-generated from routine',
                        completed=False
                    )
                    created_sessions.append(session)

            return created_sessions

        except Exception as e:
            logging.error(f"Error generating sessions: {str(e)}")
            raise RoutineValidationError(f"Failed to generate sessions: {str(e)}")