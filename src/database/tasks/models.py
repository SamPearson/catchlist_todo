from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.base.models import PrincipledMixin
from src.database.db import db
from src.database.base.models import UserOwnedModel, TaggableMixin


class Task(UserOwnedModel, TaggableMixin, PrincipledMixin):
    """
    Task model representing both standalone tasks and project tasks.
    """
    __tablename__ = "tasks"

    title = Column(String(200), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, default=False)
    completed_at = Column(db.DateTime)
    status = Column(String(20), default='open')  # open, waiting, deferred, declined, stale
    active = Column(Boolean, default=True)
    
    # Optional project association
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")

    def as_dict(self):
        """Convert task to dictionary representation"""
        data = super().as_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'active': self.active,
            'project_id': self.project_id,
            'tags': [tag.as_dict() for tag in self.tags],
            'principles': [p.as_dict() for p in self.principles]
        })
        return data