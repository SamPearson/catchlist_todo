
from datetime import datetime
from sqlalchemy.sql import func
from ...config.db_setup import db  # deprecated model, db handling

class Tag(db.Model):
    """
    Tag model representing user-defined tags for categorizing items.
    Designed to be attachable to tasks and other future entities.
    """
    __tablename__ = 'new_tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(10), default='#6c757d')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # named new_tags to avoid collision and help identify cruft, rename during cleanup
    user = db.relationship('User', back_populates='tags')

    def as_dict(self):
        """Convert tag to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }