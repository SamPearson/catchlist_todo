from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import RoutineSession as RoutineSession
from .repository import SessionRepo
from src.database.base.exceptions import ValidationError


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
            timezone=data.get('timezone', 'UTC'),
            completed=data.get('completed', False),
            notes=data.get('notes'),
            rpe=data.get('rpe')
        )

    def update_session(self, session_id: int, user_id: int, data: Dict[str, Any]) -> Optional[RoutineSession]:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return None

        updatable = ['start_time', 'end_time', 'completed', 'notes', 'rpe', 'timezone']
        update_data = {k: v for k, v in data.items() if k in updatable}

        return self.repo.update(session_obj, **update_data)

    def delete_session(self, session_id: int, user_id: int) -> bool:
        session_obj = self.get_session(session_id, user_id)
        if not session_obj:
            return False
        return self.repo.delete(session_obj)