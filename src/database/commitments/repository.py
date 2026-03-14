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

    def search(
        self,
        *,
        user_id: int,
        timeframe_id: int | None = None,
        timeframe_ids: list[int] | None = None,
        target_type: str | None = None,
        target_types: list[str] | None = None,
        target_id: int | None = None,
        status: str | None = None,
        statuses: list[str] | None = None,
        is_hard: bool | None = None,
        due_after: datetime | None = None,
        due_before: datetime | None = None,
    ) -> list[Commitment]:
        """
        Flexible search for commitments with multiple filter dimensions.

        Args:
            user_id: Required user ID
            timeframe_id: Single timeframe to filter by
            timeframe_ids: Multiple timeframes to filter by (OR condition)
            target_type: Single target type to filter by
            target_types: Multiple target types to filter by (OR condition)
            target_id: Specific target ID to filter by
            status: Single status to filter by
            statuses: Multiple statuses to filter by (OR condition)
            is_hard: True = has due_at_utc, False = no due_at_utc, None = both
            due_after: Filter for due_at_utc >= this value
            due_before: Filter for due_at_utc < this value

        Returns:
            List of commitments matching all provided filters
        """
        query = self.session.query(Commitment).filter_by(user_id=user_id)

        # Timeframe filters
        if timeframe_id is not None:
            query = query.filter(Commitment.timeframe_id == timeframe_id)
        elif timeframe_ids is not None and len(timeframe_ids) > 0:
            query = query.filter(Commitment.timeframe_id.in_(timeframe_ids))

        # Target type filters
        if target_type is not None:
            query = query.filter(Commitment.target_type == target_type)
        elif target_types is not None and len(target_types) > 0:
            query = query.filter(Commitment.target_type.in_(target_types))

        # Target ID filter
        if target_id is not None:
            query = query.filter(Commitment.target_id == target_id)

        # Status filters
        if status is not None:
            query = query.filter(Commitment.status == status)
        elif statuses is not None and len(statuses) > 0:
            query = query.filter(Commitment.status.in_(statuses))

        # Hard vs soft filter
        if is_hard is True:
            query = query.filter(Commitment.due_at_utc.isnot(None))
        elif is_hard is False:
            query = query.filter(Commitment.due_at_utc.is_(None))

        # Date range filters
        if due_after is not None:
            query = query.filter(Commitment.due_at_utc >= due_after)
        if due_before is not None:
            query = query.filter(Commitment.due_at_utc < due_before)

        # Order by due date (nulls last), then created date
        query = query.order_by(
            Commitment.due_at_utc.asc().nulls_last(),
            Commitment.created_at.asc()
        )

        return query.all()