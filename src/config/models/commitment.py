from datetime import datetime
from ..db_setup import db

class Commitment(db.Model):
    __tablename__ = 'commitment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, nullable=False)  # ID of the task (ProjectTask or CatchlistItem)
    entity_type = db.Column(db.String(50), nullable=False)  # 'project_task' or 'catchlist_item'
    
    due_date = db.Column(db.Date, nullable=False)  # When it's due
    start_date = db.Column(db.Date, nullable=True)  # Optional start date
    eta = db.Column(db.String(50))  # Estimated time to complete
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_task(self):
        """Get the associated task object based on entity_type"""
        if self.entity_type == 'project_task':
            from .project import ProjectTask
            return ProjectTask.query.get(self.task_id)
        elif self.entity_type == 'catchlist_item':
            from .catchlist import CatchlistItem
            return CatchlistItem.query.get(self.task_id)
        return None
    
    def as_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "entity_type": self.entity_type,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "eta": self.eta,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 