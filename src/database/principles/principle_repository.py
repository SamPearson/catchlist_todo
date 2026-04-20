from typing import Optional, List
from sqlalchemy.orm import Session
from src.database.base.base_repositories import UserOwnedRepository
from .principle_models import Principle

class PrincipleRepo(UserOwnedRepository[Principle]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Principle)

    def find_by_title(self, user_id: int, title: str) -> Optional[Principle]:
        return self.session.query(Principle).filter_by(user_id=user_id, title=title).first()

    def exists_by_title(self, title: str, user_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if a tag with the given title exists for a user"""
        query = self.session.query(Principle).filter_by(title=title, user_id=user_id)
        if exclude_id is not None:
            query = query.filter(Principle.id != exclude_id)
        return query.first() is not None
