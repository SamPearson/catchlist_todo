from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import foreign
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Project(db.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    win_condition = Column(Text)
    reason = Column(Text)
    next_step = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)
    
    # Relationships
    tasks = relationship('ProjectTask', back_populates='project', cascade='all, delete-orphan')
    checkins = relationship(
        'Checkin',
        primaryjoin="and_(Checkin.entity_type=='project', foreign(Checkin.entity_id)==Project.id)",
        cascade='all, delete-orphan'
    )
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "win_condition": self.win_condition,
            "reason": self.reason,
            "next_step": self.next_step,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProjectTask(db.Model):
    __tablename__ = 'project_task'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    complete = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    on_daily_todo = Column(Boolean, default=False)
    
    # Relationships
    project = relationship('Project', back_populates='tasks')
    checkins = relationship(
        'Checkin',
        primaryjoin="and_(Checkin.entity_type=='project_task', foreign(Checkin.entity_id)==ProjectTask.id)",
        cascade='all, delete-orphan'
    )
    
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "complete": self.complete,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 