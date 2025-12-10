from datetime import datetime
from sqlalchemy.sql import func
from src.database.db import db  # deprecated model, db handling


from src.database.base.models import UserOwnedModel
from sqlalchemy import Column, Text, Boolean


class Task(UserOwnedModel):
    """Task model representing user tasks (formerly known as catchlist items)."""

    content = Column(Text, nullable=False)
    completed = Column(Boolean, default=False)

    def as_dict(self):
        """Convert task to dictionary representation"""
        data = super().as_dict()
        data.update({
            'content': self.content,
            'completed': self.completed
        })
        return data