from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship


class Commitment(db.Model):
    """
    A Commitment represents a user's intention to complete a task or catchlist item
    by a specific date. It may have a start time and is assigned to a specific day.
    """
    __tablename__ = 'commitment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # The item this commitment refers to - only one will be set
    project_task_id = db.Column(db.Integer, db.ForeignKey('project_task.id'), nullable=True)
    catchlist_item_id = db.Column(db.Integer, db.ForeignKey('catchlist_item.id'), nullable=True)
    
    # Scheduling info
    due_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)  # Optional start time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status tracking
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    rpe = db.Column(db.Integer, nullable=True)  # Rate of Perceived Exertion (1-10)
    notes = db.Column(db.Text)
    
    # Relationships
    project_task = relationship("ProjectTask", foreign_keys=[project_task_id])
    catchlist_item = relationship("CatchlistItem", foreign_keys=[catchlist_item_id])
    
    @property
    def item_type(self):
        """Returns the type of item this commitment refers to"""
        if self.project_task_id:
            return "project_task"
        elif self.catchlist_item_id:
            return "catchlist_item"
        return None
    
    @property
    def item(self):
        """Returns the actual item this commitment refers to"""
        if self.project_task_id:
            return self.project_task
        elif self.catchlist_item_id:
            return self.catchlist_item
        return None
        
    @property
    def title(self):
        """Returns a title for this commitment based on the associated item"""
        if self.project_task_id:
            return self.project_task.title
        elif self.catchlist_item_id:
            return self.catchlist_item.content
        return "Untitled commitment" 