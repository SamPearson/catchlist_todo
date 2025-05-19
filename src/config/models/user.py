from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..db_setup import db
from ..db_config import Config
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Relationships
    commitments = relationship("Commitment", back_populates="user", lazy=True)
    soft_commitments = relationship("SoftCommitment", back_populates="user", lazy=True)
    projects = relationship("Project", back_populates="user", lazy=True)
    catchlist_items = relationship("CatchlistItem", back_populates="user", lazy=True)
    routines = relationship("Routine", back_populates="user", lazy=True)
    sessions = relationship("Session", back_populates="user", lazy=True)
    checkins = relationship("Checkin", back_populates="user", lazy=True)
    
    # Relationships will be defined as backref from their respective models
    # to avoid circular imports
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class BlacklistedToken(db.Model):
    __tablename__ = 'blacklisted_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def clean_expired(cls):
        """Remove tokens that are past their JWT expiration time"""
        expiration = datetime.utcnow() - Config.get_token_expires_delta()
        cls.query.filter(cls.created_at < expiration).delete()
        db.session.commit() 