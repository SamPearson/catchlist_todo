from datetime import datetime
from ..db_setup import db


class Comment(db.Model):
    """
    A Comment represents user feedback or notes on various entities.
    """
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rpe = db.Column(db.Integer)  # 1-10 rating if applicable
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    entity_type = db.Column(db.String(50), nullable=False)  # 'execution_record', 'project_task', 'catchlist_item', etc.
    entity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def as_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "rpe": self.rpe,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M'),
            "entity_type": self.entity_type,
            "entity_id": self.entity_id
        } 