from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .db_config import Config
from .db_setup import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True,
                            cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BlacklistedToken(db.Model):
    __tablename__ = 'blacklisted_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def clean_expired(cls):
        """Remove tokens that are past their JWT expiration time"""
        # Your JWT expiration time + a small buffer
        expiration = datetime.utcnow() - Config.get_token_expires_delta()
        cls.query.filter(cls.created_at < expiration).delete()
        db.session.commit()


class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "complete": self.complete
        }


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    win_condition = db.Column(db.Text)
    reason = db.Column(db.Text)
    next_step = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtasks = db.relationship('ProjectSubtask', backref='project', lazy=True, cascade="all, delete-orphan")


class ProjectSubtask(db.Model):
    __tablename__ = 'project_subtask'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    on_daily_todo = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)


class CatchListEntry(db.Model):
    __tablename__ = 'catchlist_entry'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, archived, someday
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_event'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)  # Calendar UID
    summary = db.Column(db.String(200))
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    rrule = db.Column(db.String(200))  # For recurring events
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executions = db.relationship('EventExecution', backref='event', lazy=True)


class EventExecution(db.Model):
    __tablename__ = 'event_execution'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('calendar_event.id'), nullable=False)
    execution_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.String(20))  # yes, no, or missed
    rpe = db.Column(db.Integer)  # 1-10 rating
    notes = db.Column(db.Text)