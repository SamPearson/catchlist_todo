from typing import Optional
from sqlalchemy.orm import Session
from src.database.base.repositories import UserOwnedRepository
from .models import Routine

class RoutineRepo(UserOwnedRepository[Routine]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Routine)

    def find_by_external_uid(self, user_id: int, external_uid: str) -> Optional[Routine]:
        """Find a routine by its external calendar UID (used for syncing)"""
        return (
            self.session.query(Routine)
            .filter_by(user_id=user_id, external_uid=external_uid)
            .first()
        )