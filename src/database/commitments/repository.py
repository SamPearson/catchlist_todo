from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from src.database.base.repositories import UserOwnedRepository
from src.database.commitments.models import Commitment


class CommitmentRepo(UserOwnedRepository[Commitment]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Commitment)

    def find_by_unique(
        self,
        *,
        user_id: int,
        target_type: str,
        target_id: int,
        timeframe_id: int,
    ) -> Commitment | None:
        return (
            self.session.query(Commitment)
            .filter_by(
                user_id=user_id,
                target_type=target_type,
                target_id=target_id,
                timeframe_id=timeframe_id,
            )
            .one_or_none()
        )

    def list_for_timeframe(self, *, user_id: int, timeframe_id: int) -> list[Commitment]:
        return (
            self.session.query(Commitment)
            .filter_by(user_id=user_id, timeframe_id=timeframe_id)
            .order_by(Commitment.due_at_utc.asc().nulls_last(), Commitment.created_at.asc())
            .all()
        )

    def list_for_target(self, *, user_id: int, target_type: str, target_id: int) -> list[Commitment]:
        return (
            self.session.query(Commitment)
            .filter_by(user_id=user_id, target_type=target_type, target_id=target_id)
            .order_by(Commitment.created_at.desc())
            .all()
        )

    def list_hard_in_window(
        self, *, user_id: int, start_utc: datetime, end_utc: datetime
    ) -> list[Commitment]:
        return (
            self.session.query(Commitment)
            .filter(
                Commitment.user_id == user_id,
                Commitment.due_at_utc.isnot(None),
                Commitment.due_at_utc >= start_utc,
                Commitment.due_at_utc < end_utc,
            )
            .order_by(Commitment.due_at_utc.asc())
            .all()
        )