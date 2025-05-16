from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import foreign

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    win_condition = db.Column(db.Text)
    reason = db.Column(db.Text)
    next_step = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    tasks = db.relationship('ProjectTask', backref='project', lazy=True, cascade="all, delete-orphan")
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "win_condition": self.win_condition,
            "reason": self.reason,
            "next_step": self.next_step,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProjectTask(db.Model):
    __tablename__ = 'project_task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    complete = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='project_task', foreign(Comment.entity_id)==ProjectTask.id)",
        backref="project_task",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "complete": self.complete,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 