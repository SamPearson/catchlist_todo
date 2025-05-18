from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship, foreign

class Routine(db.Model):
    """
    A Routine represents a recurring activity that the user wants to perform regularly.
    """
    __tablename__ = 'routine'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    rrule = db.Column(db.String(200))  # For recurring events
    active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # External calendar integration 
    external_uid = db.Column(db.String(100))  # Calendar UID for external syncing
    external_source = db.Column(db.String(50))  # e.g., 'caldav', 'google'
    
    # Relationships
    sessions = relationship('Session', backref='routine', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super(Routine, self).__init__(**kwargs)
        print(f"Initializing Routine with kwargs: {kwargs}")  # Debug log
        if 'title' not in kwargs:
            raise ValueError("title is required")
        if not kwargs['title']:
            raise ValueError("title cannot be empty")
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "rrule": self.rrule,
            "active": self.active,
            "external_uid": self.external_uid,
            "external_source": self.external_source
        }


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
    checkins = relationship('Checkin', 
                          primaryjoin="and_(foreign(Checkin.entity_id)==Session.id, "
                                    "Checkin.entity_type=='session')",
                          lazy=True,
                          cascade="all, delete-orphan",
                          overlaps="checkins,checkins,checkins")
    notes = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Rate of Perceived Exertion (1-10)
    
    @property
    def duration_minutes(self):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return 0 