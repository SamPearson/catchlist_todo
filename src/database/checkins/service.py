from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.database.checkins.models import CheckinRecord
from src.database.checkins.repository import CheckinRepo


@dataclass(frozen=True)
class CheckinValidationError(Exception):
    message: str


@dataclass(frozen=True)
class CheckinTargetNotFound(Exception):
    message: str


class CheckinService:
    """
    Enforces:
    - valid target_type
    - note required
    - target exists and belongs to user (for all supported targets)
    
    All datetime parameters should be in UTC. Timezone conversion
    is handled by the API layer.
    """

    ALLOWED_TARGET_TYPES = {"task", "project", "routine", "session", "report", "tag", "principle"}

    def __init__(self, session: Session):
        self.session = session
        self.repo = CheckinRepo(session=session)

    def _normalize_target_type(self, target_type: str) -> str:
        t = (target_type or "").strip().lower()
        if t not in self.ALLOWED_TARGET_TYPES:
            raise CheckinValidationError(
                f"Invalid target_type '{target_type}'. Allowed: {', '.join(sorted(self.ALLOWED_TARGET_TYPES))}."
            )
        return t

    def _normalize_note(self, note: str) -> str:
        n = (note or "").strip()
        if not n:
            raise CheckinValidationError("note is required.")
        return n

    def _target_exists(self, *, user_id: int, target_type: str, target_id: int) -> bool:
        """
        Existence + ownership check per target type.
        """
        if target_id <= 0:
            return False

        if target_type == "task":
            from src.database.tasks.models import Task
            return self.session.query(Task).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "project":
            from src.database.projects.models import Project
            return self.session.query(Project).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "routine":
            from src.database.routines.models import Routine
            return self.session.query(Routine).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "session":
            from src.database.sessions.models import RoutineSession
            return self.session.query(RoutineSession).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "report":
            from src.database.reports.models import Report
            return self.session.query(Report).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "tag":
            from src.database.tags.models import Tag
            return self.session.query(Tag).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "principle":
            from src.database.principles.models import Principle
            return self.session.query(Principle).filter_by(id=target_id, user_id=user_id).first() is not None

        return False

    def create(
        self,
        *,
        user_id: int,
        target_type: str,
        target_id: int,
        note: str,
        occurred_at_utc: datetime | None = None,
    ) -> CheckinRecord:
        """
        Create a checkin record.
        
        Args:
            user_id: Owner of the checkin
            target_type: One of the allowed target types
            target_id: ID of the target entity
            note: Required checkin note
            occurred_at_utc: When this occurred (UTC). Defaults to now if not provided.
        """
        ttype = self._normalize_target_type(target_type)
        n = self._normalize_note(note)

        if occurred_at_utc is None:
            occurred_at_utc = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))

        if not self._target_exists(user_id=user_id, target_type=ttype, target_id=int(target_id)):
            raise CheckinTargetNotFound(f"Target not found for {ttype} id={target_id}")

        return self.repo.create(
            user_id=user_id,
            target_type=ttype,
            target_id=int(target_id),
            note=n,
            occurred_at_utc=occurred_at_utc,
        )

    def get(self, *, user_id: int, checkin_id: int) -> CheckinRecord | None:
        return self.repo.get(checkin_id, user_id=user_id)

    def update(
            self,
            *,
            user_id: int,
            checkin_id: int,
            note: str | None = None,
            occurred_at_utc: datetime | None = None,
    ) -> CheckinRecord | None:
        """
        Update a checkin record.

        Args:
            user_id: The user ID
            checkin_id: The checkin ID
            note: Optional new note text
            occurred_at_utc: Optional new occurred_at timestamp (UTC)

        Returns:
            Updated CheckinRecord or None if not found

        Raises:
            CheckinValidationError: If validation fails
        """
        checkin = self.get(user_id=user_id, checkin_id=checkin_id)
        if not checkin:
            return None

        update_data = {}

        if note is not None:
            update_data['note'] = self._normalize_note(note)

        if occurred_at_utc is not None:
            update_data['occurred_at_utc'] = occurred_at_utc

        if not update_data:
            return checkin  # No changes needed

        return self.repo.update(checkin, **update_data)

    def delete(self, *, user_id: int, checkin_id: int) -> bool:
        checkin = self.get(user_id=user_id, checkin_id=checkin_id)
        if not checkin:
            return False
        self.repo.delete(checkin)
        return True

    def list_for_target(
        self,
        *,
        user_id: int,
        target_type: str,
        target_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CheckinRecord]:
        ttype = self._normalize_target_type(target_type)

        if not self._target_exists(user_id=user_id, target_type=ttype, target_id=int(target_id)):
            raise CheckinTargetNotFound(f"Target not found for {ttype} id={target_id}")

        return self.repo.list_for_target(
            user_id=user_id,
            target_type=ttype,
            target_id=int(target_id),
            limit=limit,
            offset=offset,
        )