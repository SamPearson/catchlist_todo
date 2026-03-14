from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint

from src.database.base.base_models import UserOwnedModel


class Commitment(UserOwnedModel):
    """
    A commitment attaches exactly one target (polymorphic) to exactly one timeframe.

    - Soft commitment: timeframe_id is the chosen timeframe; due_at_utc/start_at_utc are NULL
    - Hard commitment: timeframe_id is the derived DAY timeframe; due_at_utc required; start_at_utc optional
    """
    __tablename__ = "commitments"

    timeframe_id = Column(Integer, ForeignKey("timeframes.id"), nullable=False, index=True)

    target_type = Column(String(32), nullable=False, index=True)  # task|project|routine|session
    target_id = Column(Integer, nullable=False, index=True)

    # planned|done|skipped|canceled|missed
    status = Column(String(16), nullable=False, default="planned", index=True)

    notes = Column(Text, nullable=True)

    # Hard timing (UTC instants). Soft commitments keep these NULL.
    start_at_utc = Column(DateTime(timezone=True), nullable=True, index=True)
    due_at_utc = Column(DateTime(timezone=True), nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "target_type",
            "target_id",
            "timeframe_id",
            name="uq_commitments_user_target_timeframe",
        ),
        Index(
            "ix_commitments_user_type_id_due",
            "user_id",
            "target_type",
            "target_id",
            "due_at_utc",
        ),
    )

    def as_dict(self):
        data = super().as_dict()
        data.update(
            {
                "timeframe_id": self.timeframe_id,
                "target_type": self.target_type,
                "target_id": self.target_id,
                "status": self.status,
                "notes": self.notes,
                "start_at_utc": self.start_at_utc.isoformat() if self.start_at_utc else None,
                "due_at_utc": self.due_at_utc.isoformat() if self.due_at_utc else None,
            }
        )
        return data