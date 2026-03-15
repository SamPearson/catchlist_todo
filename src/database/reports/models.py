from sqlalchemy import (
    Column, Integer, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from src.database.base.base_models import UserOwnedModel


class Report(UserOwnedModel):
    """
    Report linked 1:1 with a Timeframe for planning and reflection.
    
    Reports store user-created planning and reflection content.
    Commitments and other derived data are queried dynamically, not stored.
    """
    __tablename__ = "reports"

    timeframe_id = Column(Integer, ForeignKey('timeframes.id'), nullable=False, unique=True)

    # Planning and reflection text fields (user-editable)
    plan = Column(Text)
    reason = Column(Text)
    pre_notes = Column(Text)
    post_notes = Column(Text)

    # Relationships
    timeframe = relationship("Timeframe", backref="report", uselist=False)

    __table_args__ = (
        UniqueConstraint("timeframe_id", name="uq_reports_timeframe"),
    )

    def as_dict(self):
        """
        Minimal API representation of a report.
        Returns only the user-created content fields.
        For full representation including commitments/stats, use service methods.
        """
        return {
            'plan': self.plan,
            'reason': self.reason,
            'pre_notes': self.pre_notes,
            'post_notes': self.post_notes,
        }

    def as_dict_full(self):
        """
        Full representation including metadata and timeframe.
        Does not include commitments/stats - those should be added by service layer.
        """
        data = super().as_dict()
        data.update({
            'timeframe_id': self.timeframe_id,
            'plan': self.plan,
            'reason': self.reason,
            'pre_notes': self.pre_notes,
            'post_notes': self.post_notes,
            'timeframe': self.timeframe.as_dict() if self.timeframe else None,
        })
        return data