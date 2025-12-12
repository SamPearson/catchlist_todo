from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.database.base.models import UserOwnedModel
from src.database.db import db


class TagAssociation(db.Model):
    """Association model for connecting tags to any entity"""
    __tablename__ = 'tag_association'

    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id', ondelete='CASCADE'), nullable=False)
    entity_id = Column(Integer, nullable=False)
    entity_type = Column(String(50), nullable=False)

    # Index for faster lookups - combine with extend_existing
    __table_args__ = (
        db.Index('idx_tag_entity', 'entity_type', 'entity_id'),
    )


class Tag(UserOwnedModel):
    """Tag model representing user-defined tags"""
    __tablename__ = 'tag'

    name = Column(String(50), nullable=False)
    color = Column(String(10), default='#6c757d')

    associations = relationship("TagAssociation",
                              backref='tag',
                              cascade='all, delete-orphan')

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'name': self.name,
            'color': self.color
        })
        return data