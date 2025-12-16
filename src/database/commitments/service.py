from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.config.models.user import User
from src.database.commitments.models import Commitment
from src.database.commitments.repository import CommitmentRepo
from src.database.timeframes.service import TimeframeService


@dataclass(frozen=True)
class CommitmentConflict(Exception):
    message: str


@dataclass(frozen=True)
class CommitmentValidationError(Exception):
    message: str


class CommitmentService:
    ALLOWED_TARGET_TYPES = {"task", "project", "routine", "session"}
    ALLOWED_STATUSES = {"planned", "done", "skipped", "canceled", "missed"}

    def __init__(self, session: Session):
        self.session = session
        self.repo = CommitmentRepo(session=session)
        self.timeframe_service = TimeframeService(session=session)

    def _get_user_timezone(self, user_id: int) -> str:
        user = User.query.get(user_id)
        return (user.timezone if user and getattr(user, "timezone", None) else "UTC")

    def _normalize_status(self, status: str | None) -> str:
        if not status:
            return "planned"
        s = status.strip().lower()
        if s not in self.ALLOWED_STATUSES:
            raise CommitmentValidationError(
                f"Invalid status '{status}'. Allowed: {', '.join(sorted(self.ALLOWED_STATUSES))}."
            )
        return s

    def _normalize_target_type(self, target_type: str) -> str:
        t = (target_type or "").strip().lower()
        if t not in self.ALLOWED_TARGET_TYPES:
            raise CommitmentValidationError(
                f"Invalid target_type '{target_type}'. Allowed: {', '.join(sorted(self.ALLOWED_TARGET_TYPES))}."
            )
        return t

    def _parse_iso_datetime(self, value: str, user_tz: str) -> datetime:
        """
        Accepts ISO datetime strings. If naive, interpret as user local time and convert to UTC.
        """
        try:
            dt = datetime.fromisoformat(value)
        except Exception:
            raise CommitmentValidationError("Invalid datetime format. Expected ISO 8601.")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(user_tz))

        return dt.astimezone(ZoneInfo("UTC"))

    def _anchor_for_day(self, start_at_utc: datetime | None, due_at_utc: datetime) -> datetime:
        return start_at_utc or due_at_utc

    def create_soft(
        self,
        *,
        user_id: int,
        target_type: str,
        target_id: int,
        timeframe_id: int,
        status: str | None = None,
        notes: str | None = None,
    ) -> Commitment:
        target_type = self._normalize_target_type(target_type)
        status = self._normalize_status(status)

        existing = self.repo.find_by_unique(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=timeframe_id,
        )
        if existing is not None:
            raise CommitmentConflict("Soft commitment already exists for this target and timeframe.")

        return self.repo.create(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=timeframe_id,
            status=status,
            notes=notes,
            start_at_utc=None,
            due_at_utc=None,
        )

    def create_hard(
        self,
        *,
        user_id: int,
        target_type: str,
        target_id: int,
        due_at: str,
        start_at: str | None = None,
        status: str | None = None,
        notes: str | None = None,
    ) -> Commitment:
        target_type = self._normalize_target_type(target_type)
        status = self._normalize_status(status)

        user_tz = self._get_user_timezone(user_id)

        due_at_utc = self._parse_iso_datetime(due_at, user_tz=user_tz)
        start_at_utc = self._parse_iso_datetime(start_at, user_tz=user_tz) if start_at else None

        anchor_utc = self._anchor_for_day(start_at_utc, due_at_utc)
        anchor_local_day = anchor_utc.astimezone(ZoneInfo(user_tz)).date()

        # Hard commitments always attach to the derived DAY timeframe.
        day_tf = self.timeframe_service.get_or_create_for_local_date(
            user_id=user_id,
            kind=TimeframeService.KIND_DAY,
            local_day=anchor_local_day,
            user_tz=user_tz,
        )

        existing = self.repo.find_by_unique(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=day_tf.id,
        )
        if existing is not None:
            raise CommitmentConflict("Hard commitment already exists for this target on that day.")

        return self.repo.create(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=day_tf.id,
            status=status,
            notes=notes,
            start_at_utc=start_at_utc,
            due_at_utc=due_at_utc,
        )

    def get(self, *, user_id: int, commitment_id: int) -> Commitment | None:
        return self.repo.get(commitment_id, user_id=user_id)

    def delete(self, *, user_id: int, commitment_id: int) -> bool:
        c = self.get(user_id=user_id, commitment_id=commitment_id)
        if not c:
            return False
        self.repo.delete(c)
        return True

    def set_status(self, *, user_id: int, commitment_id: int, status: str) -> Commitment | None:
        c = self.get(user_id=user_id, commitment_id=commitment_id)
        if not c:
            return None
        normalized = self._normalize_status(status)
        return self.repo.update(c, status=normalized)

    def list(self, *, user_id: int, timeframe_id: int | None = None) -> list[Commitment]:
        if timeframe_id is not None:
            return self.repo.list_for_timeframe(user_id=user_id, timeframe_id=timeframe_id)
        return self.repo.list_for_user(user_id=user_id)