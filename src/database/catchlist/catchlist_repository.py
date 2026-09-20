from typing import Optional

from sqlalchemy.orm import Session

from src.database.base.base_repositories import UserOwnedRepository
from src.database.catchlist.catchlist_models import Catchlist


class CatchlistRepository(UserOwnedRepository[Catchlist]):
    """Repository for the per-user catch list singleton."""

    def __init__(self, db_session: Session):
        super().__init__(session=db_session, model_class=Catchlist)

    def get_for_user(self, user_id: int) -> Optional[Catchlist]:
        """Retrieve the catch list for a user, or None if none exists yet."""
        return (
            self.session.query(Catchlist)
            .filter_by(user_id=user_id)
            .first()
        )

    def create_for_user(self, user_id: int, content: str = "") -> Catchlist:
        """Create a new catch list row for a user."""
        return super().create(user_id=user_id, content=content)

    def update_for_user(self, user_id: int, content: str) -> Catchlist:
        """Upsert the catch list content for a user.

        Returns the existing row updated with the new content, or creates
        the row if the user does not have one yet.
        """
        catchlist = self.get_for_user(user_id)
        if catchlist is None:
            return self.create_for_user(user_id=user_id, content=content)
        return super().update(user_id, catchlist.id, content=content)