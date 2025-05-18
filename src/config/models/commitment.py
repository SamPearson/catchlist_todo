from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship, foreign

class Commitment(db.Model):
    """
    A Commitment represents a user's intention to complete a task or catchlist item
    by a specific date. It tracks progress through checkins.
    """
    __tablename__ = 'commitment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # The item this commitment refers to - only one will be set
    project_task_id = db.Column(db.Integer, db.ForeignKey('project_task.id'), nullable=True)
    catchlist_item_id = db.Column(db.Integer, db.ForeignKey('catchlist_item.id'), nullable=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    
    # Scheduling info
    due_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)  # Optional start time
    end_time = db.Column(db.DateTime, nullable=True)  # Optional end time
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Status tracking
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="commitments")
    project_task = relationship("ProjectTask", foreign_keys=[project_task_id])
    catchlist_item = relationship("CatchlistItem", foreign_keys=[catchlist_item_id])
    routine = relationship("Routine", foreign_keys=[routine_id])
    session = relationship("Session", foreign_keys=[session_id])
    checkins = relationship("Checkin", 
                          primaryjoin="and_(foreign(Checkin.entity_id)==Commitment.id, "
                                    "Checkin.entity_type=='commitment')",
                          lazy=True,
                          cascade="all, delete-orphan",
                          overlaps="checkins,checkins,checkins,checkins")
    
    @property
    def item_type(self):
        """Returns the type of item this commitment refers to"""
        if self.project_task_id:
            return "project_task"
        elif self.catchlist_item_id:
            return "catchlist_item"
        elif self.routine_id:
            return "routine"
        return None
    
    @property
    def item(self):
        """Returns the actual item this commitment refers to"""
        if self.project_task_id:
            return self.project_task
        elif self.catchlist_item_id:
            return self.catchlist_item
        elif self.routine_id:
            return self.routine
        return None
    
    @property
    def title(self):
        """Returns a title for this commitment based on the associated item"""
        if self.project_task_id:
            return self.project_task.title
        elif self.catchlist_item_id:
            return self.catchlist_item.content
        elif self.routine_id:
            return self.routine.title
        return "Untitled commitment"
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "item_type": self.item_type,
            "item": self.item.as_dict() if self.item else None,
            "checkins": [checkin.as_dict() for checkin in self.checkins]
        }
