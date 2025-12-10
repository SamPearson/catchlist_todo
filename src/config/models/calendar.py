from datetime import datetime
from src.database.db import db
from sqlalchemy.orm import relationship

class Calendar(db.Model):
    """
    A Calendar represents an imported calendar from a CalDAV source.
    """
    __tablename__ = 'calendar'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    color = db.Column(db.String(7), default='#767676')  # Hex color code
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    external_uid = db.Column(db.String(100))  # Calendar UID for external syncing
    external_source = db.Column(db.String(50))  # e.g., 'caldav', 'google'
    
    # Relationships
    user = relationship('User', back_populates='calendars')
    routines = relationship('Routine', back_populates='calendar', cascade='all, delete-orphan')
    
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "external_uid": self.external_uid,
            "external_source": self.external_source
        } 