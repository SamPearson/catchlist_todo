from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship


class Routine(db.Model):
    """
    A Routine represents a recurring plan to do something on a schedule.
    This replaces the old CalendarEvent model.
    """
    __tablename__ = 'routine'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)  # Calendar UID
    summary = db.Column(db.String(200))
    description = db.Column(db.Text)
    rrule = db.Column(db.String(200))  # For recurring events
    active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sessions = relationship('Session', backref='routine', lazy=True, cascade="all, delete-orphan")


class Session(db.Model):
    """
    A Session is a specific instance of a Routine, representing a planned activity 
    at a specific time. Previous instances were stored in CalendarEvent.
    """
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checkins = relationship('Checkin', backref='session', lazy=True, cascade="all, delete-orphan")
    notes = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Rate of Perceived Exertion (1-10)
    
    @property
    def duration_minutes(self):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return 0 