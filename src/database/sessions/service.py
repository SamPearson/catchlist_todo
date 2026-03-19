from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import RoutineSession
from .repository import SessionRepo
from src.database.base.exceptions import ValidationError
from src.database.routines.models import Routine
from src.database.commitments.service import CommitmentService, CommitmentConflict
from src.database.tags.service import TagService
from src.database.principles.service import PrincipleService
from src.database.timeframes.service import TimeframeService
from src.database.users.models import User
from src.utils.timezone import from_utc
from dateutil.rrule import rrulestr, YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MO, TU, WE, TH, FR, SA, SU
import logging


class SessionValidationError(ValidationError):
    pass


class SessionService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = SessionRepo(session)
        self.commitment_service = CommitmentService(session)
        self.tag_service = TagService(session)
        self.principle_service = PrincipleService(session)
        self.timeframe_service = TimeframeService(session)

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
            from src.utils.timezone import utc_to_local_date, compute_timeframe_bounds

            # Get the local date for the session's end time
            local_date = utc_to_local_date(session_obj.end_time, user_tz)

            # Compute day timeframe bounds
            start_utc, end_utc, label = compute_timeframe_bounds(
                kind="day",
                local_day=local_date,
                user_tz=user_tz,
            )

            # Get or create the day timeframe
            timeframe = self.timeframe_service.get_or_create_for_bounds(
                user_id=user_id,
                kind="day",
                start_utc=start_utc,
                end_utc=end_utc,
                label=label,
            )

            # Create hard commitment directly (no special method needed)
            self.commitment_service.create_hard(
                user_id=user_id,
                target_type="session",
                target_id=session_obj.id,
                timeframe_id=timeframe.id,
                start_at_utc=session_obj.start_time,
                due_at_utc=session_obj.end_time,
                status="planned",
                notes=None,
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

    def create_session(self, user_id: int, routine_id: int, data: Dict[str, Any],
                      inherit_tags: bool = True, inherit_principles: bool = True) -> RoutineSession:
        if not data.get('start_time') or not data.get('end_time'):
            raise SessionValidationError("Start and end times are required for sessions")

        # Get the routine to fetch its title
        routine = self.session.query(Routine).filter_by(id=routine_id, user_id=user_id).first()
        if not routine:
            raise SessionValidationError(f"Routine with ID {routine_id} not found")

        session_obj = self.repo.create(
            user_id=user_id,
            routine_id=routine_id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            status=data.get('status', 'scheduled'),
            notes=data.get('notes'),
            rpe=data.get('rpe')
        )


        # Inherit tags from routine if requested
        if inherit_tags:
            self._inherit_tags(routine_id, session_obj, user_id)

        # Inherit principles from routine if requested
        if inherit_principles:
            self._inherit_principles(routine_id, session_obj, user_id)

        # Auto-create commitment for the session
        user_tz = self._get_user_timezone(user_id)
        self._create_commitment_for_session(user_id, session_obj, user_tz)

        return session_obj

    def _inherit_tags(self, routine_id: int, session_obj: RoutineSession, user_id: int) -> None:
        """
        Copy tags from a routine to a session using the tag service.

        Args:
            routine_id: ID of the routine to inherit from
            session_obj: The session object to inherit into
            user_id: ID of the user (for ownership validation)
        """
        try:
            routine = self.session.query(Routine).filter_by(id=routine_id).first()
            if not routine:
                logging.warning(f"Routine {routine_id} not found for tag inheritance")
                return

            # Use TagService to properly add each tag via TagAssociation
            if routine.tags:
                for tag in routine.tags:
                    self.tag_service.add_tag_to_entity(tag.id, user_id, session_obj)
                logging.debug(f"Inherited {len(routine.tags)} tags to session {session_obj.id}")
        except Exception as e:
            logging.error(f"Error inheriting tags: {str(e)}")
            # Don't raise; this is non-critical to session creation

    def _inherit_principles(self, routine_id: int, session_obj: RoutineSession, user_id: int) -> None:
        """
        Copy principles from a routine to a session using the principle service.

        Args:
            routine_id: ID of the routine to inherit from
            session_obj: The session object to inherit into
            user_id: ID of the user (for ownership validation)
        """
        try:
            routine = self.session.query(Routine).filter_by(id=routine_id).first()
            if not routine:
                logging.warning(f"Routine {routine_id} not found for principle inheritance")
                return

            # Use PrincipleService to properly add each principle via PrincipleAssociation
            if routine.principles:
                for principle in routine.principles:
                    self.principle_service.attach_to_entity(principle.id, user_id, session_obj)
                logging.debug(f"Inherited {len(routine.principles)} principles to session {session_obj.id}")
        except Exception as e:
            logging.error(f"Error inheriting principles: {str(e)}")
            # Don't raise; this is non-critical to session creation


    def update_session(self, session_id: int, user_id: int, data: Dict[str, Any]) -> Optional[RoutineSession]:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return None

        # Exclude status from updates; use set_session_status() instead
        updatable = ['start_time', 'end_time', 'notes', 'rpe']
        update_data = {k: v for k, v in data.items() if k in updatable}

        return self.repo.update(session_obj, **update_data)

    def set_session_status(self, session_id: int, user_id: int, status: str) -> Optional[RoutineSession]:
        """
        Set the status of a session to one of: scheduled, completed, skipped, cancelled

        Args:
            session_id: ID of the session
            user_id: ID of the user who owns the session
            status: One of 'scheduled', 'completed', 'skipped', 'cancelled'

        Returns:
            Updated session object or None if not found

        Raises:
            SessionValidationError if status is invalid
        """
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return None

        valid_statuses = {'scheduled', 'completed', 'skipped', 'cancelled'}
        if status not in valid_statuses:
            raise SessionValidationError(
                f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
            )

        return self.repo.update(session_obj, status=status)


    def delete_session(self, session_id: int, user_id: int) -> bool:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return False

        # Delete associated commitment first
        self._delete_commitment_for_session(user_id, session_id)

        return self.repo.delete(session_obj)


    def create_sessions_for_period(self, user_id: int, routine_id: int, start_date: datetime,
                                   end_date: datetime, inherit_tags: bool = True,
                                   inherit_principles: bool = True) -> List[RoutineSession]:
        """Create sessions for a routine based on its recurrence rule within a date range"""
        routine = self.session.query(Routine).filter_by(id=routine_id, user_id=user_id).first()
        if not routine:
            raise SessionValidationError(f"Routine with ID {routine_id} not found")

        if not routine.rrule:
            raise SessionValidationError(f"Routine has no recurrence rule")

        if not routine.start_time:
            raise SessionValidationError("Routine has no start time")

        if not routine.end_time:
            raise SessionValidationError("Routine has no end time")

        # Get user timezone for commitment creation
        user_tz = self._get_user_timezone(user_id)

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

                # Check if session already exists (duplicate prevention)
                existing = self.repo.list_for_window(
                    user_id=user_id,
                    start=session_start,
                    end=session_end
                )

                if existing:
                    logging.debug(f"Session already exists for {session_start}; skipping")
                    continue

                session_obj = self.repo.create(
                    user_id=user_id,
                    routine_id=routine_id,
                    start_time=session_start,
                    end_time=session_end,
                    status='scheduled',
                    notes='Auto-generated from routine',
                    routine_name=routine.title
                )
                created_sessions.append(session_obj)

                # Inherit tags from routine if requested
                if inherit_tags:
                    self._inherit_tags(routine_id, session_obj, user_id)

                # Inherit principles from routine if requested
                if inherit_principles:
                    self._inherit_principles(routine_id, session_obj, user_id)

                # Auto-create commitment for each generated session
                self._create_commitment_for_session(user_id, session_obj, user_tz)

            logging.info(f"Generated {len(created_sessions)} sessions for routine {routine_id}")
            return created_sessions

        except Exception as e:
            logging.error(f"Error generating sessions: {str(e)}")
            raise SessionValidationError(f"Failed to generate sessions: {str(e)}")


    def _parse_rrule(self, rrule_str: str, start_date: datetime) -> dict:
        """Parse RRULE string into dateutil parameters"""
        rrule_parts = {'dtstart': start_date, 'freq': WEEKLY}

        freq_map = {
            'YEARLY': YEARLY,
            'MONTHLY': MONTHLY,
            'WEEKLY': WEEKLY,
            'DAILY': DAILY,
            'HOURLY': HOURLY
        }

        weekday_map = {
            'MO': MO,
            'TU': TU,
            'WE': WE,
            'TH': TH,
            'FR': FR,
            'SA': SA,
            'SU': SU
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