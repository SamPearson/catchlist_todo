from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.db import db
from src.database.base.models import UserOwnedModel, TaggableMixin


class RoutineSession(UserOwnedModel, TaggableMixin):
    """
    A Session is a specific instance of a Routine occurring at a specific time.
    It tracks completion, notes, and performance (RPE).
    """
    __tablename__ = "sessions"

    routine_id = Column(Integer, ForeignKey('routines.id'), nullable=False)

    # Timing (stored in UTC)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)

    # Tracking
    completed = Column(Boolean, default=False)
    notes = Column(Text)
    rpe = Column(Integer)  # Rate of Perceived Exertion (1-10)

    # Relationships
    routine = relationship("Routine", back_populates="sessions")

    @property
    def duration_minutes(self):
        """Calculate duration in minutes between start and end time"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return 0

    def as_dict(self):
        """
        Return a dictionary representation of the model.
        Datetime values are returned in ISO format (UTC).
        """
        data = super().as_dict()
        data.update({
            'routine_id': self.routine_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'completed': self.completed,
            'notes': self.notes,
            'rpe': self.rpe,
            'duration_minutes': self.duration_minutes
        })
        return data