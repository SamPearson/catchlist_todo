from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Time
from sqlalchemy.orm import relationship

from database.base.models import PrincipledMixin
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
    start_time = Column(Time, nullable=True)  # Time of day when the routine starts
    end_time = Column(Time, nullable=True)    # Time of day when the routine ends
    active = Column(Boolean, default=True)

    # External Integration Metadata
    external_uid = Column(String(100), index=True)
    external_source = Column(String(50))  # e.g., 'caldav', 'manual'
    external_source_name = Column(String(100))

    # Optional connection to a Calendar entity
    calendar_id = Column(Integer, ForeignKey('calendars.id'), nullable=True)

    # Relationships
    calendar = relationship("Calendar", back_populates="routines")
    sessions = relationship("RoutineSession", back_populates="routine", cascade="all, delete-orphan")

    def get_rrule(self):
        """
        Returns a dateutil.rrule object based on the stored rrule string.
        
        Note: Since we only store time components, the RRULE's start date 
        should be provided by the caller when generating occurrences.
        """
        if not self.rrule or not self.start_time:
            return None

        from dateutil.rrule import rrulestr
        from datetime import datetime, date
        # Use today's date with our time for RRULE creation
        # The actual dates will be determined by the RRULE pattern
        base_date = datetime.combine(date.today(), self.start_time)
        return rrulestr(self.rrule, dtstart=base_date)

    def as_dict(self):
        """
        Return a dictionary representation of the model.
        Times are returned in HH:MM format.
        """
        data = super().as_dict()
        data.update({
            "title": self.title,
            "description": self.description,
            "rrule": self.rrule,
            "start_time": self.start_time.strftime('%H:%M') if self.start_time else None,
            "end_time": self.end_time.strftime('%H:%M') if self.end_time else None,
            "active": self.active,
            "external_uid": self.external_uid,
            "external_source": self.external_source,
            "external_source_name": self.external_source_name,
            "calendar_id": self.calendar_id,
            "tags": [tag.as_dict() for tag in self.tags],
            "principles": [p.as_dict() for p in self.principles]
        })
        return data