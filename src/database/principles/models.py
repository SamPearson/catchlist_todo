from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database.base.models import UserOwnedModel
from src.database.db import db

class PrincipleAssociation(db.Model):
    """Association model for connecting principles to any entity"""
    __tablename__ = 'principle_associations'

    id = Column(Integer, primary_key=True)
    principle_id = Column(Integer, ForeignKey('principles.id', ondelete='CASCADE'), nullable=False)
    entity_id = Column(Integer, nullable=False)
    entity_type = Column(String(50), nullable=False)

    __table_args__ = (
        db.Index('idx_principle_entity', 'entity_type', 'entity_id'),
    )

class Principle(UserOwnedModel):
    """
    Principle model representing high-level 'Platonic Ideals'.
    Similar to tags, but used for high-order behavioral alignment.
    """
    __tablename__ = 'principles'

    title = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(10), default='#ffd700')  # Default to gold

    associations = relationship("PrincipleAssociation",
                              backref='principle',
                              cascade='all, delete-orphan')

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'color': self.color
        })
        return data