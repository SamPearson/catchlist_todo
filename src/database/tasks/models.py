from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.database.db import db
from src.database.base.models import UserOwnedModel, TaggableMixin


class Task(UserOwnedModel, TaggableMixin):
    """
    Task model representing both standalone tasks and project tasks.
    """
    title = Column(String(200), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, default=False)
    completed_at = Column(db.DateTime)
    
    # Optional project association
    project_id = Column(Integer, ForeignKey('project.id'), nullable=True)
    
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
            'project_id': self.project_id,
            'tags': [tag.as_dict() for tag in self.tags]
        })
        return data