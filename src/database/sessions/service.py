from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import RoutineSession
from .repository import SessionRepo
from src.database.base.exceptions import ValidationError
from src.database.routines.models import Routine
from dateutil import rrule as dateutil_rrule
import logging


class SessionValidationError(ValidationError):
    pass


class SessionService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = SessionRepo(session)

    def get_session(self, session_id: int, user_id: int) -> Optional[RoutineSession]:
        return self.repo.get(session_id, user_id)

    def list_sessions_for_window(self, user_id: int, start: datetime, end: datetime) -> List[RoutineSession]:
        return self.repo.list_for_window(user_id, start, end)

    def create_session(self, user_id: int, routine_id: int, data: Dict[str, Any]) -> RoutineSession:
        if not data.get('start_time') or not data.get('end_time'):
            raise SessionValidationError("Start and end times are required for sessions")

        return self.repo.create(
            user_id=user_id,
            routine_id=routine_id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            completed=data.get('completed', False),
            status=data.get('status', 'scheduled'),
            notes=data.get('notes'),
            rpe=data.get('rpe')
        )

    def update_session(self, session_id: int, user_id: int, data: Dict[str, Any]) -> Optional[RoutineSession]:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return None

        updatable = ['start_time', 'end_time', 'completed', 'status', 'notes', 'rpe']
        update_data = {k: v for k, v in data.items() if k in updatable}

        # If completed is being set to True, auto-set status to 'completed' if not already set
        if update_data.get('completed') is True:
            if 'status' not in update_data and session_obj.status != 'completed':
                update_data['status'] = 'completed'

        return self.repo.update(session_obj, **update_data)

    def delete_session(self, session_id: int, user_id: int) -> bool:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return False
        return self.repo.delete(session_obj)

    def create_sessions_for_period(self, user_id: int, routine_id: int, start_date: datetime, 
                                 end_date: datetime) -> List[RoutineSession]:
        """Create sessions for a routine based on its recurrence rule within a date range"""
        routine = self.session.query(Routine).filter_by(id=routine_id, user_id=user_id).first()
        if not routine:
            raise SessionValidationError(f"Routine with ID {routine_id} not found")

        if not routine.rrule:
            raise SessionValidationError(f"Routine has no recurrence rule")

        if not routine.start_time:
            raise SessionValidationError("Routine has no start time")

        # Calculate session duration from routine
        duration_minutes = 0
        if routine.end_time:
            # Calculate minutes between start and end time
            duration_minutes = (
                (routine.end_time.hour * 60 + routine.end_time.minute) - 
                (routine.start_time.hour * 60 + routine.start_time.minute)
            )
        if duration_minutes <= 0:
            duration_minutes = 30  # Default duration

        # Parse the RRULE
        rrule_parts = self._parse_rrule(routine.rrule, start_date)

        # Generate dates
        dates = list(dateutil_rrule.rrule(**rrule_parts))
        
        # Create sessions for each date
        created_sessions = []
        for date in dates:
            # Create datetimes for this occurrence
            session_start = datetime.combine(date.date(), routine.start_time)
            session_end = session_start + timedelta(minutes=duration_minutes)

            # Skip if outside our window
            if session_start < start_date or session_start > end_date:
                continue

            try:
                session = self.create_session(user_id, routine_id, {
                    'start_time': session_start,
                    'end_time': session_end,
                    'notes': 'Auto-generated from routine'
                })
                created_sessions.append(session)
            except Exception as e:
                logging.error(f"Error creating session: {str(e)}")

        return created_sessions

    def _parse_rrule(self, rrule_str: str, start_date: datetime) -> dict:
        """Parse RRULE string into dateutil parameters"""
        rrule_parts = {'dtstart': start_date, 'freq': dateutil_rrule.WEEKLY}

        freq_map = {
            'YEARLY': dateutil_rrule.YEARLY,
            'MONTHLY': dateutil_rrule.MONTHLY,
            'WEEKLY': dateutil_rrule.WEEKLY,
            'DAILY': dateutil_rrule.DAILY,
            'HOURLY': dateutil_rrule.HOURLY
        }

        weekday_map = {
            'MO': dateutil_rrule.MO,
            'TU': dateutil_rrule.TU,
            'WE': dateutil_rrule.WE,
            'TH': dateutil_rrule.TH,
            'FR': dateutil_rrule.FR,
            'SA': dateutil_rrule.SA,
            'SU': dateutil_rrule.SU
        }

        parts = rrule_str.split(';')
        for part in parts:
            if '=' not in part:
                continue
            key, value = part.split('=', 1)
            
            if key == 'FREQ' and value in freq_map:
                rrule_parts['freq'] = freq_map[value]
            elif key == 'INTERVAL':
                try:
                    rrule_parts['interval'] = int(value)
                except ValueError:
                    pass
            elif key == 'BYDAY':
                weekdays = [weekday_map[day] for day in value.split(',') 
                           if day.strip().upper() in weekday_map]
                if weekdays:
                    rrule_parts['byweekday'] = weekdays if len(weekdays) > 1 else weekdays[0]

        return rrule_parts