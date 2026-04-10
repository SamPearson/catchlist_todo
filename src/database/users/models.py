from datetime import datetime

from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from src.database.db import db
from src.database.config_db import Config

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=db.func.now())

    timezone = db.Column(db.String(64), nullable=False, default="UTC")

    # Add cascade delete to all relationships
    tasks = relationship('Task', back_populates='user', cascade='all, delete-orphan')
    projects = relationship('Project', back_populates='user', cascade='all, delete-orphan')
    tags = relationship('Tag', back_populates='user', cascade='all, delete-orphan')
    principles = relationship('Principle', back_populates='user', cascade='all, delete-orphan')
    calendars = relationship('Calendar', back_populates='user', cascade='all, delete-orphan')
    routine = relationship("Routine", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("RoutineSession", back_populates="user", cascade="all, delete-orphan")
    timeframes = relationship("Timeframe", back_populates="user", cascade="all, delete-orphan")
    commitment = relationship("Commitment", back_populates="user", cascade="all, delete-orphan")
    checkin = relationship("CheckinRecord", back_populates="user", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class BlacklistedToken(db.Model):
    __tablename__ = 'blacklisted_tokens'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def clean_expired(cls):
        """Remove tokens that are past their JWT expiration time"""
        expiration = datetime.utcnow() - Config.get_token_expires_delta()
        cls.query.filter(cls.created_at < expiration).delete()
        db.session.commit()