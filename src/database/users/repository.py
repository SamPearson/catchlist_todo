from typing import Optional
from sqlalchemy.orm import Session
from src.database.base.repositories import BaseRepository
from .models import User


class UserRepository(BaseRepository[User]):
    """Repository for handling User database operations"""

    def __init__(self, session: Session):
        super().__init__(session=session, model_class=User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username"""
        try:
            return self.session.query(User).filter_by(username=username).first()
        except Exception as e:
            from src.database.base.exceptions import RepositoryError
            raise RepositoryError(f"Error retrieving user by username: {str(e)}")

    def username_exists(self, username: str) -> bool:
        """Check if a username already exists"""
        return self.get_by_username(username) is not None

    def create_user(self, username: str, password: str, name: Optional[str] = None,
                    timezone: str = "UTC") -> User:
        """Create a new user with hashed password"""
        user = User()
        user.username = username
        user.set_password(password)
        if name:
            user.name = name
        user.timezone = timezone

        self.session.add(user)
        self.session.commit()
        return user

    def update_password(self, user: User, new_password: str) -> User:
        """Update a user's password"""
        user.set_password(new_password)
        self.session.commit()
        return user

    def update_timezone(self, user: User, timezone: str) -> User:
        """Update a user's timezone"""
        return self.update(user, timezone=timezone)