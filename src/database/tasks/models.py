from datetime import datetime
from sqlalchemy.sql import func
from ...config.db_setup import db  # deprecated model, db handling

class Task(db.Model):
    """
    Task model representing user tasks (formerly known as catchlist items).
    Designed to be extensible for future features like tags and checkins.
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


    def as_dict(self):
        """Convert task to dictionary representation"""
        return {
            'id': self.id,
            'content': self.content,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }