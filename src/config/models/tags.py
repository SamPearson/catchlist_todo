from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.sql import func

# Tag model for user-defined tags
class Tag(db.Model):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    color = Column(String(10), default="#6c757d")  # Default color in hex
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship('User', back_populates='tags')
    routine_associations = relationship('RoutineTag', back_populates='tag', cascade='all, delete-orphan')
    session_associations = relationship('SessionTag', back_populates='tag', cascade='all, delete-orphan')
    project_associations = relationship('ProjectTag', back_populates='tag', cascade='all, delete-orphan')
    project_task_associations = relationship('ProjectTaskTag', back_populates='tag', cascade='all, delete-orphan')
    catchlist_item_associations = relationship('CatchlistItemTag', back_populates='tag', cascade='all, delete-orphan')
    
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Tag associations for different entities

class RoutineTag(db.Model):
    __tablename__ = 'routine_tag'
    routine_id = Column(Integer, ForeignKey('routine.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    routine = relationship('Routine', back_populates='tag_associations')
    tag = relationship('Tag', back_populates='routine_associations')

class SessionTag(db.Model):
    __tablename__ = 'session_tag'
    session_id = Column(Integer, ForeignKey('session.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    session = relationship('Session', back_populates='tag_associations')
    tag = relationship('Tag', back_populates='session_associations')

class ProjectTag(db.Model):
    __tablename__ = 'project_tag'
    project_id = Column(Integer, ForeignKey('project.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship('Project', back_populates='tag_associations')
    tag = relationship('Tag', back_populates='project_associations')

class ProjectTaskTag(db.Model):
    __tablename__ = 'project_task_tag'
    project_task_id = Column(Integer, ForeignKey('project_task.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project_task = relationship('ProjectTask', back_populates='tag_associations')
    tag = relationship('Tag', back_populates='project_task_associations')

class CatchlistItemTag(db.Model):
    __tablename__ = 'catchlist_item_tag'
    catchlist_item_id = Column(Integer, ForeignKey('catchlist_item.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    catchlist_item = relationship('CatchlistItem', back_populates='tag_associations')
    tag = relationship('Tag', back_populates='catchlist_item_associations') 