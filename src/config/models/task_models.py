from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship, foreign


class Project(db.Model):
    """
    A Project represents a large goal that will take many actions to complete.
    """
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    win_condition = db.Column(db.Text)
    reason = db.Column(db.Text)
    next_step = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = relationship('ProjectTask', backref='project', lazy=True, cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)


class ProjectTask(db.Model):
    """
    A ProjectTask is a single action that will push towards a project goal.
    Renamed from ProjectSubtask.
    """
    __tablename__ = 'project_task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Comments relationship defined through the Comment model
    comments = relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='project_task', foreign(Comment.entity_id)==ProjectTask.id)",
        backref="project_task",
        lazy=True,
        cascade="all, delete-orphan"
    ) 