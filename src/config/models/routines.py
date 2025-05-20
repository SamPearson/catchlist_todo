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
    external_source_name = db.Column(db.String(100))  # Name of the source calendar
    
    # Relationships
    user = relationship('User', back_populates='routines')
    sessions = relationship('Session', backref='routine', lazy=True, cascade="all, delete-orphan")
    tag_associations = relationship('RoutineTag', back_populates='routine', cascade='all, delete-orphan')
    
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
            "external_source": self.external_source,
            "external_source_name": self.external_source_name,
            "tags": [assoc.tag.as_dict() for assoc in self.tag_associations] if hasattr(self, 'tag_associations') else []
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
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    checkins = relationship('Checkin', 
                          primaryjoin="and_(foreign(Checkin.entity_id)==Session.id, "
                                    "Checkin.entity_type=='session')",
                          lazy=True,
                          cascade="all, delete-orphan",
                          overlaps="checkins,checkins,checkins")
    tag_associations = relationship('SessionTag', back_populates='session', cascade='all, delete-orphan')
    notes = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Rate of Perceived Exertion (1-10)
    
    @property
    def duration_minutes(self):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return 0
        
    def as_dict(self):
        base_dict = {
            "id": self.id,
            "routine_id": self.routine_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "completed": self.completed,
            "notes": self.notes,
            "rpe": self.rpe,
            "duration_minutes": self.duration_minutes
        }
        
        # Add tags if they exist
        if hasattr(self, 'tag_associations'):
            base_dict["tags"] = [assoc.tag.as_dict() for assoc in self.tag_associations]
        
        return base_dict 