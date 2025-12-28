from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.config.models.user import User
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
    """

    ALLOWED_TARGET_TYPES = {"task", "project", "routine", "session", "commitment"}

    def __init__(self, session: Session):
        self.session = session
        self.repo = CheckinRepo(session=session)

    def _get_user_timezone(self, user_id: int) -> str:
        user = User.query.get(user_id)
        return (user.timezone if user and getattr(user, "timezone", None) else "UTC")

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

    def _parse_occurred_at(self, occurred_at: str | None, user_tz: str) -> datetime:
        """
        Accept ISO datetime string. If naive, interpret in user's timezone and convert to UTC.
        If omitted, default to now (UTC).
        """
        if not occurred_at:
            return datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))

        try:
            dt = datetime.fromisoformat(occurred_at)
        except Exception:
            raise CheckinValidationError("Invalid occurred_at format. Expected ISO 8601 datetime.")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(user_tz))

        return dt.astimezone(ZoneInfo("UTC"))

    def _target_exists(self, *, user_id: int, target_type: str, target_id: int) -> bool:
        """
        Existence + ownership check per target type.

        NOTE: routines/sessions are currently legacy models (src.config.*) in your codebase;
        this function intentionally enforces existence anyway, per your updated decision.
        """
        if target_id <= 0:
            return False

        if target_type == "task":
            from src.database.tasks.models import Task  # new system
            return self.session.query(Task).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "project":
            from src.database.projects.models import Project  # new system
            return self.session.query(Project).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "commitment":
            from src.database.commitments.models import Commitment  # new system (your current name)
            return self.session.query(Commitment).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "routine":
            from database.routines.models import Routine
            return self.session.query(Routine).filter_by(id=target_id, user_id=user_id).first() is not None

        if target_type == "session":
            from database.sessions.models import RoutineSession
            return self.session.query(RoutineSession).filter_by(id=target_id, user_id=user_id).first() is not None

        return False

    def create(
        self,
        *,
        user_id: int,
        target_type: str,
        target_id: int,
        note: str,
        occurred_at: str | None = None,
    ) -> CheckinRecord:
        ttype = self._normalize_target_type(target_type)
        n = self._normalize_note(note)

        user_tz = self._get_user_timezone(user_id)
        occurred_at_utc = self._parse_occurred_at(occurred_at, user_tz=user_tz)

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
            occurred_at: str | None = None,
    ) -> CheckinRecord | None:
        """
        Update a checkin record.

        Args:
            user_id: The user ID
            checkin_id: The checkin ID
            note: Optional new note text
            occurred_at: Optional new occurred_at timestamp (ISO format)

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

        if occurred_at is not None:
            user_tz = self._get_user_timezone(user_id)
            update_data['occurred_at_utc'] = self._parse_occurred_at(occurred_at, user_tz=user_tz)

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