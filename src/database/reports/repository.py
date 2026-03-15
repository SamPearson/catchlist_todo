from __future__ import annotations

from sqlalchemy.orm import Session

from src.database.base.repositories import UserOwnedRepository
from src.database.reports.models import Report


class ReportRepo(UserOwnedRepository[Report]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Report)

    def find_by_timeframe(self, *, user_id: int, timeframe_id: int) -> Report | None:
        """Find a report by its timeframe ID."""
        return (
            self.session.query(Report)
            .filter_by(user_id=user_id, timeframe_id=timeframe_id)
            .one_or_none()
        )

    def list_by_timeframes(self, *, user_id: int, timeframe_ids: list[int]) -> list[Report]:
        """Get reports for multiple timeframes."""
        return (
            self.session.query(Report)
            .filter(Report.user_id == user_id, Report.timeframe_id.in_(timeframe_ids))
            .all()
        )