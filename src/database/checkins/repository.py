from __future__ import annotations

from sqlalchemy.orm import Session

from src.database.base.repositories import UserOwnedRepository
from src.database.checkins.models import CheckinRecord


class CheckinRepo(UserOwnedRepository[CheckinRecord]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=CheckinRecord)

    def list_for_target(
        self,
        *,
        user_id: int,
        target_type: str,
        target_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CheckinRecord]:
        return (
            self.session.query(CheckinRecord)
            .filter_by(user_id=user_id, target_type=target_type, target_id=target_id)
            .order_by(CheckinRecord.occurred_at_utc.desc(), CheckinRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )