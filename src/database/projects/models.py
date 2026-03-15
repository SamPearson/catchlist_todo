from typing import Dict, Any

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from src.database.db import db
from src.database.base.base_models import UserOwnedModel, TaggableMixin, PrincipledMixin


class Project(UserOwnedModel, TaggableMixin, PrincipledMixin):
    """
    Project model representing long-term goals that consist of multiple tasks.
    """

    __tablename__ = "projects"

    title = Column(String(200), nullable=False)
    description = Column(Text)
    win_condition = Column(Text)
    reason = Column(Text)
    next_step = Column(String(200))
    completed = Column(Boolean, default=False)
    completed_at = Column(db.DateTime)
    status = Column(String(20), default='open')  # open, waiting, deferred, declined, stale
    active = Column(Boolean, default=True)

    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    def as_dict(self) -> Dict[str, Any]:
        """Convert Project model to dictionary representation."""
        data = super().as_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'win_condition': self.win_condition,
            'reason': self.reason,
            'next_step': self.next_step,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'active': self.active,
            'tags': [tag.as_dict() for tag in self.tags],
            'principles': [p.as_dict() for p in self.principles]
        })
        return data