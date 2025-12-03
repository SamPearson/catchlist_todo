from typing import TypeVar, Generic, Optional, List, Type, Any
from sqlalchemy.orm import Session
from .models import BaseModel
from .exceptions import RepositoryError

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Generic base repository implementing common database operations.
    """

    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    def get(self, id: int) -> Optional[T]:
        """Retrieve a record by ID."""
        try:
            return self.session.query(self.model_class).get(id)
        except Exception as e:
            raise RepositoryError(f"Error retrieving {self.model_class.__name__}: {str(e)}")

    def list(self, **filters) -> List[T]:
        """List all records matching the filters."""
        try:
            query = self.session.query(self.model_class)
            if filters:
                query = query.filter_by(**filters)
            return query.all()
        except Exception as e:
            raise RepositoryError(f"Error listing {self.model_class.__name__}: {str(e)}")

    def create(self, **data) -> T:
        """Create a new record."""
        try:
            instance = self.model_class(**data)
            self.session.add(instance)
            self.session.commit()
            return instance
        except Exception as e:
            self.session.rollback()
            raise RepositoryError(f"Error creating {self.model_class.__name__}: {str(e)}")

    def update(self, instance: T, **data) -> T:
        """Update an existing record."""
        try:
            for key, value in data.items():
                setattr(instance, key, value)
            self.session.commit()
            return instance
        except Exception as e:
            self.session.rollback()
            raise RepositoryError(f"Error updating {self.model_class.__name__}: {str(e)}")

    def delete(self, instance: T) -> bool:
        """Delete a record."""
        try:
            self.session.delete(instance)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise RepositoryError(f"Error deleting {self.model_class.__name__}: {str(e)}")

class UserOwnedRepository(BaseRepository[T]):
    """
    Repository for user-owned models with additional user filtering.
    """

    def get(self, id: int, user_id: int) -> Optional[T]:
        """Retrieve a record by ID and user_id."""
        try:
            return self.session.query(self.model_class).filter_by(
                id=id,
                user_id=user_id
            ).first()
        except Exception as e:
            raise RepositoryError(f"Error retrieving {self.model_class.__name__}: {str(e)}")

    def list_for_user(self, user_id: int, **filters) -> List[T]:
        """List all records for a specific user."""
        filters['user_id'] = user_id
        return super().list(**filters)