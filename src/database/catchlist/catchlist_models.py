from __future__ import annotations

from sqlalchemy import Column, Text, UniqueConstraint

from src.database.base.base_models import UserOwnedModel


class Catchlist(UserOwnedModel):
    """
    Per-user catch list: a single free-form text blob for capturing
    half-formed ideas, tasks, projects, and other stray thoughts
    (a GTD-style brain dump). Each user has exactly one row.
    """
    __tablename__ = "catchlists"

    content = Column(Text, nullable=False, default="")

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_catchlists_user_id"),
    )

    def as_dict(self):
        data = super().as_dict()
        data.update(
            {
                "content": self.content,
            }
        )
        return data