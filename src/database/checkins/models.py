from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from src.database.base.models import UserOwnedModel


class CheckinRecord(UserOwnedModel):
    """
    New-system checkin model.

    - Attaches a note to exactly one target entity (polymorphic).
    - occurred_at_utc is the event time (not necessarily created_at).
    """
    __tablename__ = "checkins"

    target_type = Column(String(32), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)

    note = Column(Text, nullable=False)

    occurred_at_utc = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index(
            "ix_checkins_user_target_time",
            "user_id",
            "target_type",
            "target_id",
            "occurred_at_utc",
        ),
    )

    def as_dict(self):
        data = super().as_dict()
        data.update(
            {
                "target_type": self.target_type,
                "target_id": self.target_id,
                "note": self.note,
                "occurred_at_utc": self.occurred_at_utc.isoformat() if self.occurred_at_utc else None,
            }
        )
        return data