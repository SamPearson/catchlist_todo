from datetime import datetime
from ..db_setup import db
from sqlalchemy.orm import relationship, foreign

class Checkin(db.Model):
    """
    A Checkin represents a timestamped update on any entity's progress,
    including a comment, RPE rating, and optional metrics.
    """
    __tablename__ = 'checkin'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # The entity this checkin refers to
    entity_type = db.Column(db.String(50), nullable=False)  # 'commitment', 'project_task', 'catchlist_item', 'session', etc.
    entity_id = db.Column(db.Integer, nullable=False)
    
    # Time block relationship
    time_block_id = db.Column(db.Integer, db.ForeignKey('time_block.id'), nullable=True)
    
    # Core checkin data
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    comment = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Rate of Perceived Exertion (1-10)
    
    # Optional metrics
    progress = db.Column(db.Integer)  # Optional progress percentage
    mood = db.Column(db.Integer)  # Optional mood rating
    energy = db.Column(db.Integer)  # Optional energy level
    gains = db.Column(db.Text)  # Optional gains/achievements
    gratitudes = db.Column(db.Text)  # Optional gratitudes
    
    # Relationships
    user = relationship("User", back_populates="checkins")
    time_block = relationship("TimeBlock", back_populates="checkins")
    
    def as_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "comment": self.comment,
            "rpe": self.rpe,
            "progress": self.progress,
            "mood": self.mood,
            "energy": self.energy,
            "gains": self.gains,
            "gratitudes": self.gratitudes,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "time_block_id": self.time_block_id
        } 