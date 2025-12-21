from typing import Optional, List
from sqlalchemy.orm import Session
from src.database.base.repositories import UserOwnedRepository
from .models import Principle

class PrincipleRepo(UserOwnedRepository[Principle]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Principle)

    def find_by_title(self, user_id: int, title: str) -> Optional[Principle]:
        return self.session.query(Principle).filter_by(user_id=user_id, title=title).first()