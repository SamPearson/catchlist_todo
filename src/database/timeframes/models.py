from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, String, UniqueConstraint

from src.database.base.base_models import UserOwnedModel
from src.database.db import db


class Timeframe(UserOwnedModel):
    """
    Persisted, user-scoped timeframe with UTC boundaries.

    Interval semantics are half-open: [start_at_utc, end_at_utc)
    """
    __tablename__ = "timeframes"

    kind = Column(String(16), nullable=False, index=True)

    start_at_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    end_at_utc = Column(DateTime(timezone=True), nullable=False, index=True)

    # Optional label useful for UI/debugging (e.g. "2025-W03", "Summer 2025")
    label = Column(String(32), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "kind", "start_at_utc", name="uq_timeframes_user_kind_start"),
        Index("ix_timeframes_user_kind_start_end", "user_id", "kind", "start_at_utc", "end_at_utc"),
    )

    def as_dict(self):
        data = super().as_dict()
        data.update(
            {
                "kind": self.kind,
                "start_at_utc": self.start_at_utc.isoformat() if self.start_at_utc else None,
                "end_at_utc": self.end_at_utc.isoformat() if self.end_at_utc else None,
                "label": self.label,
            }
        )
        return data