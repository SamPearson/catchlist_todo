
from datetime import datetime
from sqlalchemy.sql import func
from config.db_setup import db  # deprecated model, db handling

from database.base.models import UserOwnedModel
from sqlalchemy import Column, String


class Tag(UserOwnedModel):
    """
    Tag model representing user-defined tags for categorizing items.
    Designed to be attachable to tasks and other future entities.
    """

    name = Column(String(50), nullable=False)
    color = Column(String(10), default='#6c757d')

    def as_dict(self):
        """Convert tag to dictionary representation"""
        data = super().as_dict()
        data.update({
            'name': self.name,
            'color': self.color
        })
        return data