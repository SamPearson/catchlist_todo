from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import foreign

# Old models that we'll phase out but keep for now during migration

class ProjectSubtask(db.Model):
    __tablename__ = 'project_subtask'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    on_daily_todo = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define the relationship to comments
    comments = db.relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='project_subtask', foreign(Comment.entity_id)==ProjectSubtask.id)",
        backref="project_subtask",
        lazy=True,
        cascade="all, delete-orphan",
        overlaps="catchlist_entry,event_execution"
    )


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_event'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)  # Calendar UID
    summary = db.Column(db.String(200))
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    rrule = db.Column(db.String(200))  # For recurring events
    active = db.Column(db.Boolean, default=True)  # Whether the event is active
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executions = db.relationship('EventExecution', backref='event', lazy=True)


class BaseExecution(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    execution_date = db.Column(db.Date)
    attempted = db.Column(db.Boolean, default=True)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)


class EventExecution(BaseExecution):
    __tablename__ = 'event_execution'
    event_id = db.Column(db.Integer, db.ForeignKey('calendar_event.id'))
    rpe = db.Column(db.Integer)
    check_in_count = db.Column(db.Integer, default=0)
    
    # Define the relationship to comments
    comments = db.relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='event_execution', foreign(Comment.entity_id)==EventExecution.id)",
        backref="event_execution",
        lazy=True,
        cascade="all, delete-orphan",
        overlaps="catchlist_entry,project_subtask"
    )


class TaskExecution(BaseExecution):
    __tablename__ = 'task_execution'
    task_id = db.Column(db.Integer, db.ForeignKey('project_subtask.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    time_spent = db.Column(db.Integer)  # Minutes spent 