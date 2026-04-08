from __future__ import annotations

from datetime import datetime

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
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[CheckinRecord]:
        query = (
            self.session.query(CheckinRecord)
            .filter_by(user_id=user_id, target_type=target_type, target_id=target_id)
        )
        
        if start_date:
            query = query.filter(CheckinRecord.occurred_at_utc >= start_date)
        if end_date:
            query = query.filter(CheckinRecord.occurred_at_utc <= end_date)
        
        return (
            query
            .order_by(CheckinRecord.occurred_at_utc.desc(), CheckinRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_for_user(
        self,
        *,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[CheckinRecord]:
        """
        List all checkins for a user, optionally filtered by date range.

        Args:
            user_id: The user ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            start_date: Filter checkins on or after this date (UTC)
            end_date: Filter checkins on or before this date (UTC)

        Returns:
            List of CheckinRecords
        """
        query = self.session.query(CheckinRecord).filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(CheckinRecord.occurred_at_utc >= start_date)
        if end_date:
            query = query.filter(CheckinRecord.occurred_at_utc <= end_date)
        
        return (
            query
            .order_by(CheckinRecord.occurred_at_utc.desc(), CheckinRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def delete_for_target(
            self,
            *,
            user_id: int,
            target_type: str,
            target_id: int,
    ) -> int:
        """
        Delete all checkins for a specific target.

        Args:
            user_id: The user ID (for ownership verification)
            target_type: The target type (e.g., 'task', 'project')
            target_id: The target entity ID

        Returns:
            Number of checkins deleted
        """
        count = self.session.query(CheckinRecord).filter_by(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
        ).delete()
        self.session.commit()
        return count