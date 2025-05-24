from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship, foreign
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Text

class Commitment(db.Model):
    """
    A Commitment represents a user's intention to complete a task or catchlist item
    by a specific date. It tracks progress through checkins.
    """
    __tablename__ = 'commitment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # The item this commitment refers to - only one will be set
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    project_task_id = db.Column(db.Integer, db.ForeignKey('project_task.id'), nullable=True)
    catchlist_item_id = db.Column(db.Integer, db.ForeignKey('catchlist_item.id'), nullable=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    
    # Title and description for soft commitments
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Scheduling info
    due_date = db.Column(db.Date, nullable=True)  # Made nullable to support soft commitments
    start_time = db.Column(db.DateTime, nullable=True)  # Optional start time
    end_time = db.Column(db.DateTime, nullable=True)  # Optional end time
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Status tracking
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Soft commitment info
    is_soft_commitment = db.Column(db.Boolean, default=False)
    time_period = db.Column(db.String(20), nullable=True)  # week, month, season, year
    start_date = db.Column(db.Date, nullable=True)  # For soft commitments
    end_date = db.Column(db.Date, nullable=True)  # For soft commitments
    
    # Relationships
    user = relationship("User", back_populates="commitments")
    project = relationship("Project", foreign_keys=[project_id], back_populates="commitments")
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
        if self.project_id:
            return "project"
        elif self.project_task_id:
            return "project_task"
        elif self.catchlist_item_id:
            return "catchlist_item"
        elif self.routine_id:
            return "routine"
        return None
    
    @property
    def item(self):
        """Returns the actual item this commitment refers to"""
        if self.project_id:
            return self.project
        elif self.project_task_id:
            return self.project_task
        elif self.catchlist_item_id:
            return self.catchlist_item
        elif self.routine_id:
            return self.routine
        return None
    
    @property
    def display_title(self):
        """Returns a title for this commitment based on the associated item or stored title"""
        if self.title:
            return self.title
        if self.project_id:
            return self.project.title
        elif self.project_task_id:
            return self.project_task.title
        elif self.catchlist_item_id:
            return self.catchlist_item.content
        elif self.routine_id:
            return self.routine.title
        return "Untitled commitment"
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.display_title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "item_type": self.item_type,
            "item": self.item.as_dict() if self.item else None,
            "checkins": [checkin.as_dict() for checkin in self.checkins],
            "is_soft_commitment": self.is_soft_commitment,
            "time_period": self.time_period,
            "project_id": self.project_id,
            "project_task_id": self.project_task_id,
            "catchlist_item_id": self.catchlist_item_id,
            "routine_id": self.routine_id,
            "session_id": self.session_id
        }

class SoftCommitment(db.Model):
    """
    A SoftCommitment represents a user's intention to complete a task within a time period
    (week, month, season, or year) without a specific due date.
    """
    __tablename__ = 'soft_commitment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    time_period = db.Column(db.String(20), nullable=False)  # week, month, season, year
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Optional relationships
    project_task_id = db.Column(db.Integer, db.ForeignKey('project_task.id'), nullable=True)
    catchlist_item_id = db.Column(db.Integer, db.ForeignKey('catchlist_item.id'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="soft_commitments")
    project_task = relationship("ProjectTask", foreign_keys=[project_task_id])
    catchlist_item = relationship("CatchlistItem", foreign_keys=[catchlist_item_id])
    checkins = relationship("Checkin", 
                          primaryjoin="and_(foreign(Checkin.entity_id)==SoftCommitment.id, "
                                    "Checkin.entity_type=='soft_commitment')",
                          lazy=True,
                          cascade="all, delete-orphan")
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "time_period": self.time_period,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "project_task": self.project_task.as_dict() if self.project_task else None,
            "catchlist_item": self.catchlist_item.as_dict() if self.catchlist_item else None,
            "checkins": [checkin.as_dict() for checkin in self.checkins]
        }
