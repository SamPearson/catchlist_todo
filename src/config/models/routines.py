from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import foreign

class Routine(db.Model):
    __tablename__ = 'routine'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    rrule = db.Column(db.String(200))  # Recurrence rule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # External calendar integration 
    external_uid = db.Column(db.String(100))  # Calendar UID for external syncing
    external_source = db.Column(db.String(50))  # e.g., 'caldav', 'google'
    
    # Relationships
    sessions = db.relationship('Session', backref='routine', lazy=True, cascade="all, delete-orphan")
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "rrule": self.rrule,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "external_uid": self.external_uid,
            "external_source": self.external_source
        }


class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    checkins = db.relationship('Checkin', backref='session', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='session', foreign(Comment.entity_id)==Session.id)",
        backref="session",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def as_dict(self):
        return {
            "id": self.id,
            "routine_id": self.routine_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Checkin(db.Model):
    __tablename__ = 'checkin'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Rating of perceived exertion (1-10)
    
    def as_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "notes": self.notes,
            "rpe": self.rpe
        } 