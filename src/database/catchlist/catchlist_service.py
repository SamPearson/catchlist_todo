from sqlalchemy.orm import Session

from src.database.base.exceptions import ValidationError
from src.database.catchlist.catchlist_models import Catchlist
from .catchlist_repository import CatchlistRepository

MAX_CONTENT_LENGTH = 100000


class CatchlistValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CatchlistService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = CatchlistRepository(session)

    def get_or_create(self, user_id: int) -> Catchlist:
        """Return the user's catch list, creating an empty one if absent."""
        catchlist = self.repository.get_for_user(user_id)
        if catchlist is None:
            catchlist = self.repository.create_for_user(user_id=user_id)
        return catchlist

    def update_content(self, user_id: int, content: str) -> Catchlist:
        """Set the user's catch list content (creating the row if absent)."""
        content = content or ""
        if len(content) > MAX_CONTENT_LENGTH:
            raise CatchlistValidationError(
                f"Catch list cannot exceed {MAX_CONTENT_LENGTH} characters."
            )
        return self.repository.update_for_user(user_id=user_id, content=content)