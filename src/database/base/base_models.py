from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

from src.database.db import db

from src.utils.timezone import from_utc


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

    def as_dict(self, user_timezone: str = 'UTC') -> Dict[str, Any]:
        """
        Convert model to dictionary representation.
        
        Args:
            user_timezone: User's timezone for timestamp conversion (IANA format)
        """

        return {
            'id': self.id,
            'created_at': from_utc(self.created_at, user_timezone).isoformat() if self.created_at else None,
            'updated_at': from_utc(self.updated_at, user_timezone).isoformat() if self.updated_at else None
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
        return db.relationship(
            'User',
            backref=db.backref(
                f'{cls.__tablename__}_list',
                cascade="all, delete-orphan"
            )
        )

    def as_dict(self, user_timezone: str = 'UTC') -> Dict[str, Any]:
        """
        Convert model to dictionary representation including user_id.
        
        Args:
            user_timezone: User's timezone for timestamp conversion (IANA format)
        """
        data = super().as_dict(user_timezone=user_timezone)
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

    def as_dict(self, user_timezone: str = 'UTC') -> Dict[str, Any]:
        """
        Convert model to dictionary representation including deleted_at.
        
        Args:
            user_timezone: User's timezone for timestamp conversion (IANA format)
        """

        data = super().as_dict(user_timezone=user_timezone)
        data['deleted_at'] = from_utc(self.deleted_at, user_timezone).isoformat() if self.deleted_at else None
        return data


class TaggableMixin:
    @declared_attr
    def tags(cls):
        #Importing here to avoid circular imports
        from src.database.tags.tag_models import Tag, TagAssociation
        return db.relationship(
            "Tag",
            secondary='tag_associations',
            primaryjoin=f"and_({cls.__name__}.id==TagAssociation.entity_id, "
                       f"TagAssociation.entity_type=='{cls.__name__.lower()}')",
            secondaryjoin="Tag.id==TagAssociation.tag_id",
            lazy='select',
            backref=db.backref(f"{cls.__name__.lower()}s", lazy='dynamic')
        )


class PrincipledMixin:
    @declared_attr
    def principles(cls):
        #Importing here to avoid circular imports
        from src.database.principles.principle_models import Principle, PrincipleAssociation

        return db.relationship(
            "Principle",
            secondary='principle_associations',
            primaryjoin=f"and_({cls.__name__}.id==PrincipleAssociation.entity_id, "
                       f"PrincipleAssociation.entity_type=='{cls.__name__.lower()}')",
            secondaryjoin="Principle.id==PrincipleAssociation.principle_id",
            lazy='select',
            backref=db.backref(f"{cls.__name__.lower()}s", lazy='dynamic')
        )