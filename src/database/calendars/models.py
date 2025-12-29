from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.database.db import db
from src.database.base.models import UserOwnedModel


class Calendar(UserOwnedModel):
    """
    A Calendar represents an imported calendar from a CalDAV source.
    """
    __tablename__ = 'calendars'

    name = Column(String(200), nullable=False)
    color = Column(String(7), default='#767676')
    external_uid = Column(String(100))
    external_source = Column(String(50))

    # Relationships
    routines = relationship('Routine', back_populates='calendar', cascade='all, delete-orphan')

    def as_dict(self):
        data = super().as_dict()
        data.update({
            "name": self.name,
            "color": self.color,
            "external_uid": self.external_uid,
            "external_source": self.external_source
        })
        return data