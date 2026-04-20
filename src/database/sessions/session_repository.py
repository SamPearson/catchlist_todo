from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from src.database.base.base_repositories import UserOwnedRepository
from .session_models import RoutineSession as RoutineSession

class SessionRepo(UserOwnedRepository[RoutineSession]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=RoutineSession)

    def list_for_window(self, user_id: int, start: datetime, end: datetime) -> List[RoutineSession]:
        """Find all sessions for a user within a specific time window"""
        return (
            self.session.query(RoutineSession)
            .filter(
                RoutineSession.user_id == user_id,
                RoutineSession.start_time >= start,
                RoutineSession.start_time < end
            )
            .order_by(RoutineSession.start_time.asc())
            .all()
        )