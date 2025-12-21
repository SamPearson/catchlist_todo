from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.base.models import Principle, PrincipledMixin
from src.database.db import db
from src.database.base.models import UserOwnedModel, TaggableMixin


class Routine(UserOwnedModel, TaggableMixin, PrincipledMixin):
    """
    A Routine represents a recurring activity or a 'template' for sessions.
    It can be manually created or imported from external CalDAV calendars.
    """
    __tablename__ = "routines"

    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Recurrence and Timing
    rrule = Column(String(200))  # iCalendar recurrence rule
    timezone = Column(String(50), default="UTC")
    active = Column(Boolean, default=True)

    # External Integration Metadata
    external_uid = Column(String(100), index=True)
    external_source = Column(String(50))  # e.g., 'caldav', 'manual'
    external_source_name = Column(String(100))

    # Optional connection to a Calendar entity (if you keep the calendar model)
    calendar_id = Column(Integer, ForeignKey('calendars.id'), nullable=True)

    # Relationships
    calendar = relationship("Calendar", back_populates="routines")
    sessions = relationship("Session", back_populates="routine", cascade="all, delete-orphan")

    def as_dict(self):
        data = super().as_dict()
        data.update({
            "title": self.title,
            "description": self.description,
            "rrule": self.rrule,
            "timezone": self.timezone,
            "active": self.active,
            "external_uid": self.external_uid,
            "external_source": self.external_source,
            "external_source_name": self.external_source_name,
            "calendar_id": self.calendar_id,
            "tags": [tag.as_dict() for tag in self.tags],
            "principles": [p.as_dict() for p in self.principles]
        })
        return data