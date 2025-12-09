
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from config.db_setup import db  # TODO: Update this import when db config is moved

class BaseModel(db.Model):
    """
    Abstract base class for all models.
    Provides common fields and functionality.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name."""
        return cls.__name__.lower()

    def as_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserOwnedModel(BaseModel):
    """
    Abstract base class for models owned by a user.
    Provides user relationship and ownership validation.
    """
    __abstract__ = True

    @declared_attr
    def user_id(cls):
        return Column(Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    @declared_attr
    def user(cls):
        return db.relationship('User')

    def as_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation including user_id."""
        data = super().as_dict()
        data['user_id'] = self.user_id
        return data

class SoftDeleteModel(BaseModel):
    """
    Abstract base class for models supporting soft delete.
    Adds deleted_at timestamp.
    """
    __abstract__ = True

    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore soft-deleted record."""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft-deleted."""
        return self.deleted_at is not None

    def as_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation including deleted_at."""
        data = super().as_dict()
        data['deleted_at'] = self.deleted_at.isoformat() if self.deleted_at else None
        return data