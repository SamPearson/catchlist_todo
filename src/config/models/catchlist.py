from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import foreign

class CatchlistItem(db.Model):
    __tablename__ = 'catchlist_item'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, archived, someday
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    comments = db.relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='catchlist_item', foreign(Comment.entity_id)==CatchlistItem.id)",
        backref="catchlist_item",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def as_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        } 