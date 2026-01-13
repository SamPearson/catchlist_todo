from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import RoutineSession
from .repository import SessionRepo
from src.database.base.exceptions import ValidationError
from src.database.routines.models import Routine
from src.database.commitments.service import CommitmentService, CommitmentConflict
from src.database.users.user import User
from src.utils.timezone import from_utc
from dateutil import rrule as dateutil_rrule
import logging


class SessionValidationError(ValidationError):
    pass


class SessionService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = SessionRepo(session)
        self.commitment_service = CommitmentService(session)

    def _get_user_timezone(self, user_id: int) -> str:
        """Get the user's timezone or return UTC as default"""
        user = User.query.get(user_id)
        return user.timezone if user and hasattr(user, 'timezone') and user.timezone else "UTC"

    def _create_commitment_for_session(
        self, 
        user_id: int, 
        session_obj: RoutineSession,
        user_tz: str
    ) -> None:
        """
        Create a hard commitment for a session.
        Silently handles conflicts (commitment already exists).
        """
        try:
            # Convert UTC start time to local date for timeframe derivation
            local_start = from_utc(session_obj.start_time, user_tz)
            local_date = local_start.date()

            self.commitment_service.create_for_session(
                user_id=user_id,
                session_id=session_obj.id,
                start_at_utc=session_obj.start_time,
                due_at_utc=session_obj.end_time,
                local_date=local_date,
                user_tz=user_tz,
            )
        except CommitmentConflict:
            # Commitment already exists, that's fine
            logging.debug(f"Commitment already exists for session {session_obj.id}")
        except Exception as e:
            logging.error(f"Error creating commitment for session {session_obj.id}: {str(e)}")

    def _delete_commitment_for_session(self, user_id: int, session_id: int) -> None:
        """Delete any commitments associated with a session."""
        try:
            self.commitment_service.delete_for_target(
                user_id=user_id,
                target_type="session",
                target_id=session_id,
            )
        except Exception as e:
            logging.error(f"Error deleting commitment for session {session_id}: {str(e)}")

    def get_session(self, session_id: int, user_id: int) -> Optional[RoutineSession]:
        return self.repo.get(session_id, user_id)

    def list_sessions_for_window(self, user_id: int, start: datetime, end: datetime) -> List[RoutineSession]:
        return self.repo.list_for_window(user_id, start, end)

    def create_session(self, user_id: int, routine_id: int, data: Dict[str, Any]) -> RoutineSession:
        if not data.get('start_time') or not data.get('end_time'):
            raise SessionValidationError("Start and end times are required for sessions")

        session_obj = self.repo.create(
            user_id=user_id,
            routine_id=routine_id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            completed=data.get('completed', False),
            status=data.get('status', 'scheduled'),
            notes=data.get('notes'),
            rpe=data.get('rpe')
        )

        # Auto-create commitment for the session
        user_tz = self._get_user_timezone(user_id)
        self._create_commitment_for_session(user_id, session_obj, user_tz)

        return session_obj

    def update_session(self, session_id: int, user_id: int, data: Dict[str, Any]) -> Optional[RoutineSession]:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return None

        updatable = ['start_time', 'end_time', 'notes', 'rpe', 'status']
        update_data = {k: v for k, v in data.items() if k in updatable}

        return self.repo.update(session_obj, **update_data)

    def complete_session(self, session_id: int, user_id: int) -> Optional[RoutineSession]:
        """
        Mark a session as completed.
        Sets completed=True and status='completed'.
        """
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return None

        return self.repo.update(session_obj, completed=True, status='completed')

    def uncomplete_session(self, session_id: int, user_id: int) -> Optional[RoutineSession]:
        """
        Mark a session as not completed.
        Sets completed=False and status='scheduled'.
        """
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return None

        return self.repo.update(session_obj, completed=False, status='scheduled')

    def delete_session(self, session_id: int, user_id: int) -> bool:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return False

        # Delete associated commitment first
        self._delete_commitment_for_session(user_id, session_id)

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

        # Get user timezone for commitment creation
        user_tz = self._get_user_timezone(user_id)

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
                session_obj = self.repo.create(
                    user_id=user_id,
                    routine_id=routine_id,
                    start_time=session_start,
                    end_time=session_end,
                    completed=False,
                    status='scheduled',
                    notes='Auto-generated from routine'
                )
                created_sessions.append(session_obj)

                # Auto-create commitment for each generated session
                self._create_commitment_for_session(user_id, session_obj, user_tz)

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