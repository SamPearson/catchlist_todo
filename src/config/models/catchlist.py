from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import foreign
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class CatchlistItem(db.Model):
    __tablename__ = 'catchlist_item'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String(20), default='active')  # active, completed, archived, someday
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    checkins = relationship(
        'Checkin',
        primaryjoin="and_(Checkin.entity_type=='catchlist_item', foreign(Checkin.entity_id)==CatchlistItem.id)",
        cascade='all, delete-orphan'
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