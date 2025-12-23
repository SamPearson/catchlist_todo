from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import Routine
from .repository import RoutineRepo
from src.database.base.exceptions import ValidationError
from dateutil.rrule import rrulestr
from datetime import datetime, timedelta

from ..sessions.models import RoutineSession


class RoutineValidationError(ValidationError):
    pass


class RoutineService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = RoutineRepo(session)

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

        return self.repo.create(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            rrule=data.get('rrule'),
            timezone=data.get('timezone', 'UTC'),
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
        updatable = ['title', 'description', 'rrule', 'active', 'timezone']
        update_data = {k: v for k, v in data.items() if k in updatable}

        if 'title' in update_data and not update_data['title']:
            raise RoutineValidationError("Title cannot be empty")

        return self.repo.update(routine, **update_data)

    def delete_routine(self, routine_id: int, user_id: int) -> bool:
        routine = self.get_routine(routine_id, user_id)
        if not routine:
            return False
        return self.repo.delete(routine)

    def generate_sessions_from_rule(self, routine_id: int, user_id: int, start: datetime, end: datetime) -> int:
        """
        Uses dateutil to expand the routine's rrule into individual Session objects.
        """
        routine = self.get_routine(routine_id, user_id)
        if not routine or not routine.rrule:
            return 0
        
        from src.database.sessions.service import SessionService
        session_service = SessionService(self.session)
        
        # Use rrulestr to parse the string stored in DB
        # dtstart ensures the rule knows where to begin expanding
        rule = rrulestr(routine.rrule, dtstart=start)
        
        # Find all occurrences in the requested window
        occurrences = rule.between(start, end, inc=True)
        
        count = 0
        for dt in occurrences:
            # Check if session already exists for this exact start time 
            # (to prevent duplicates if user runs expand twice)
            existing = self.session.query(RoutineSession).filter_by(
                routine_id=routine.id, 
                start_time=dt
            ).first()
            
            if not existing:
                session_service.create_session(user_id, routine.id, {
                    "start_time": dt,
                    "end_time": dt + timedelta(minutes=30), # Default duration
                    "timezone": routine.timezone,
                    "notes": "Auto-generated from routine"
                })
                count += 1
        return count