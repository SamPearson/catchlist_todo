from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship, foreign


class Checkin(db.Model):
    """
    A Checkin is a timestamp of the user indicating they are doing the work
    in a specific session.
    """
    __tablename__ = 'checkin'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)


class DailyNote(db.Model):
    """
    A DailyNote contains notes associated with a specific day.
    """
    __tablename__ = 'daily_note'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExecutionRecord(db.Model):
    """
    An ExecutionRecord represents work completed on a specific commitment.
    This replaces the various *Execution tables from the old model.
    """
    __tablename__ = 'execution_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commitment_id = db.Column(db.Integer, db.ForeignKey('commitment.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    
    # Either commitment_id or session_id should be set
    
    execution_date = db.Column(db.Date, nullable=False)
    execution_time = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=True)
    rpe = db.Column(db.Integer, nullable=True)  # Rate of Perceived Exertion (1-10)
    notes = db.Column(db.Text)
    
    # Relationships
    commitment = relationship("Commitment", foreign_keys=[commitment_id])
    session = relationship("Session", foreign_keys=[session_id])
    
    # Comments relationship defined through the Comment model
    comments = relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='execution_record', foreign(Comment.entity_id)==ExecutionRecord.id)",
        backref="execution_record",
        lazy=True,
        cascade="all, delete-orphan"
    ) 