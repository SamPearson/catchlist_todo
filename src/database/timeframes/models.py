from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, String, UniqueConstraint

from src.database.base.base_models import UserOwnedModel
from src.database.db import db
from src.utils.timezone import from_utc


class Timeframe(UserOwnedModel):
    """
    Persisted, user-scoped timeframe with UTC boundaries.

    Interval semantics are half-open: [start_at_utc, end_at_utc)
    
    Note: Database columns are named start_at_utc/end_at_utc (stored as naive UTC),
    but as_dict() returns them as start_at/end_at (converted to user's timezone).
    """
    __tablename__ = "timeframes"

    kind = Column(String(16), nullable=False, index=True)

    start_at_utc = Column(DateTime, nullable=False, index=True)
    end_at_utc = Column(DateTime, nullable=False, index=True)

    # Optional label useful for UI/debugging (e.g. "2025-W03", "Summer 2025")
    label = Column(String(32), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "kind", "start_at_utc", name="uq_timeframes_user_kind_start"),
        Index("ix_timeframes_user_kind_start_end", "user_id", "kind", "start_at_utc", "end_at_utc"),
    )

    def as_dict(self, user_timezone: str = 'UTC'):
        """
        Convert timeframe to dictionary representation.
        Timestamps are converted to user's timezone.
        """
        data = super().as_dict(user_timezone=user_timezone)
        
        # Convert start_at_utc and end_at_utc from naive UTC to user timezone
        start_at_str = None
        if self.start_at_utc:
            local_dt = from_utc(self.start_at_utc, user_timezone)
            start_at_str = local_dt.isoformat()
        
        end_at_str = None
        if self.end_at_utc:
            local_dt = from_utc(self.end_at_utc, user_timezone)
            end_at_str = local_dt.isoformat()
        
        data.update({
            "kind": self.kind,
            "start_at": start_at_str,
            "end_at": end_at_str,
            "label": self.label,
        })
        return data