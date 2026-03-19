from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.base.base_models import PrincipledMixin
from src.database.db import db
from src.database.base.base_models import UserOwnedModel, TaggableMixin
from src.utils.timezone import from_utc


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

    def as_dict(self, user_timezone: str = 'UTC'):
        """
        Convert task to dictionary representation.
        Timestamps are converted to user's timezone.
        """

        data = super().as_dict(user_timezone=user_timezone)
        
        # Convert completed_at from naive UTC to user timezone
        completed_at_str = None
        if self.completed_at:
            # from_utc expects naive UTC datetime and returns timezone-aware
            local_dt = from_utc(self.completed_at, user_timezone)
            completed_at_str = local_dt.isoformat()
        
        data.update({
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'completed_at': completed_at_str,
            'status': self.status,
            'active': self.active,
            'project_id': self.project_id,
            'tags': [tag.as_dict() for tag in self.tags],
            'principles': [p.as_dict() for p in self.principles]
        })
        return data