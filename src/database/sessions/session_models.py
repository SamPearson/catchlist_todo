from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.db import db
from src.database.base.base_models import UserOwnedModel, TaggableMixin, PrincipledMixin


class RoutineSession(UserOwnedModel, TaggableMixin, PrincipledMixin):
    """
    A Session is a specific instance of a Routine occurring at a specific time.
    It tracks completion, notes, and performance (RPE).
    """
    __tablename__ = "sessions"

    routine_id = Column(Integer, ForeignKey('routines.id'), nullable=False)
    routine_name = Column(String(255), nullable=True)

    # Timing (stored in UTC)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)

    # Tracking
    status = Column(String(20), default='scheduled')  # scheduled, completed, skipped, cancelled
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

    def as_dict(self, user_timezone: str = 'UTC'):
        """
        Return a dictionary representation of the model.
        Datetime values are returned in ISO format (UTC).
        """
        data = super().as_dict()
        data.update({
            'routine_id': self.routine_id,
            'routine_name': self.routine_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'notes': self.notes,
            'rpe': self.rpe,
            'duration_minutes': self.duration_minutes,
            'tags': [tag.as_dict() for tag in self.tags],
            'principles': [p.as_dict() for p in self.principles]
        })
        return data