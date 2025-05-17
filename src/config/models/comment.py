from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship, foreign

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rpe = db.Column(db.Integer)  # 1-10 rating if applicable
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    entity_type = db.Column(db.String(50), nullable=False)  # 'session', 'project_task', 'catchlist_item', 'time_block'
    entity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships with back_populates to handle polymorphic relationships
    project_task = relationship(
        "ProjectTask",
        primaryjoin="and_(foreign(Comment.entity_id)==ProjectTask.id, Comment.entity_type=='project_task')",
        back_populates="comments",
        overlaps="catchlist_item,time_block"
    )
    
    catchlist_item = relationship(
        "CatchlistItem",
        primaryjoin="and_(foreign(Comment.entity_id)==CatchlistItem.id, Comment.entity_type=='catchlist_item')",
        back_populates="comments",
        overlaps="project_task,time_block"
    )
    
    time_block = relationship(
        "TimeBlock",
        primaryjoin="and_(foreign(Comment.entity_id)==TimeBlock.id, Comment.entity_type=='time_block')",
        back_populates="comments",
        overlaps="project_task,catchlist_item"
    )
    
    def get_entity(self):
        """Get the associated entity based on entity_type"""
        if self.entity_type == 'project_task':
            from .project import ProjectTask
            return ProjectTask.query.get(self.entity_id)
        elif self.entity_type == 'catchlist_item':
            from .catchlist import CatchlistItem
            return CatchlistItem.query.get(self.entity_id)
        elif self.entity_type == 'session':
            from .routines import Session
            return Session.query.get(self.entity_id)
        elif self.entity_type == 'time_block':
            from .time_blocks import TimeBlock
            return TimeBlock.query.get(self.entity_id)
        return None
    
    def as_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "rpe": self.rpe,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id
        } 