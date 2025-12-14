from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from src.database.base.repositories import UserOwnedRepository
from src.database.timeframes.models import Timeframe


class TimeframeRepo(UserOwnedRepository[Timeframe]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Timeframe)

    def find_exact(
        self,
        *,
        user_id: int,
        kind: str,
        start_at_utc: datetime,
    ) -> Timeframe | None:
        return (
            self.session.query(Timeframe)
            .filter_by(user_id=user_id, kind=kind, start_at_utc=start_at_utc)
            .one_or_none()
        )

    def find_containing(
        self,
        *,
        user_id: int,
        kind: str,
        instant_utc: datetime,
    ) -> Timeframe | None:
        return (
            self.session.query(Timeframe)
            .filter(
                Timeframe.user_id == user_id,
                Timeframe.kind == kind,
                Timeframe.start_at_utc <= instant_utc,
                Timeframe.end_at_utc > instant_utc,
            )
            .one_or_none()
        )

    def list_overlapping(
        self,
        *,
        user_id: int,
        kind: str,
        start_utc: datetime,
        end_utc: datetime,
    ) -> list[Timeframe]:
        return (
            self.session.query(Timeframe)
            .filter(
                Timeframe.user_id == user_id,
                Timeframe.kind == kind,
                Timeframe.start_at_utc < end_utc,
                Timeframe.end_at_utc > start_utc,
            )
            .order_by(Timeframe.start_at_utc.asc())
            .all()
        )