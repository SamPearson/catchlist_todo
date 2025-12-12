from datetime import datetime
from src.database.db import db
from sqlalchemy.orm import relationship, foreign


class CatchlistItem(db.Model):
    """
    A CatchlistItem is a largely unstructured piece of data. It's like a project task 
    but not associated with a project, or it may be a project itself. 
    It's an intention to do some possibly vague thing that you don't want to let go.
    Renamed from CatchListEntry.
    """
    __tablename__ = 'catchlist_item'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, archived, someday
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Comments relationship defined through the Comment model
    comments = relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='catchlist_item', foreign(Comment.entity_id)==CatchlistItem.id)",
        backref="catchlist_item",
        lazy=True,
        cascade="all, delete-orphan"
    ) 