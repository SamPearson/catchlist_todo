from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date

from sqlalchemy.orm import Session

from src.database.base.exceptions import EntityNotFoundError, InvalidStateError, ValidationError
from src.database.commitments.models import Commitment
from src.database.commitments.repository import CommitmentRepo
from src.database.timeframes.models import Timeframe
from src.database.timeframes.service import TimeframeService


@dataclass(frozen=True)
class CommitmentConflict(InvalidStateError):
    message: str


@dataclass(frozen=True)
class CommitmentValidationError(ValidationError):
    message: str


@dataclass(frozen=True)
class CommitmentTargetNotFound(EntityNotFoundError):
    message: str


@dataclass(frozen=True)
class CommitmentTimeframeNotFound(EntityNotFoundError):
    message: str


class CommitmentService:
    ALLOWED_TARGET_TYPES = {"task", "project", "routine", "session"}
    ALLOWED_STATUSES = {"planned", "done", "skipped", "canceled", "missed"}

    def __init__(self, session: Session):
        self.session = session
        self.repo = CommitmentRepo(session=session)
        self.timeframe_service = TimeframeService(session=session)

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

        return False

    def _ensure_target_exists(self, *, user_id: int, target_type: str, target_id: int) -> None:
        if not self._target_exists(user_id=user_id, target_type=target_type, target_id=int(target_id)):
            raise CommitmentTargetNotFound(f"Target not found for {target_type} id={target_id}")

    def _ensure_timeframe_exists(self, *, user_id: int, timeframe_id: int) -> None:
        if timeframe_id <= 0:
            raise CommitmentTimeframeNotFound(f"Timeframe not found id={timeframe_id}")
        tf = self.session.query(Timeframe).filter_by(id=timeframe_id, user_id=user_id).first()
        if tf is None:
            raise CommitmentTimeframeNotFound(f"Timeframe not found id={timeframe_id}")

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
        """
        Create a soft commitment (no specific time, just within a timeframe).

        Args:
            user_id: Owner of the commitment
            target_type: One of task, project, routine, session
            target_id: ID of the target entity
            timeframe_id: ID of an existing timeframe
            status: Optional status (defaults to 'planned')
            notes: Optional notes
        """
        target_type = self._normalize_target_type(target_type)
        status = self._normalize_status(status)

        self._ensure_target_exists(user_id=user_id, target_type=target_type, target_id=int(target_id))
        self._ensure_timeframe_exists(user_id=user_id, timeframe_id=int(timeframe_id))

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
            timeframe_id: int,
            due_at_utc: datetime,
            start_at_utc: datetime | None = None,
            status: str | None = None,
            notes: str | None = None,
    ) -> Commitment:
        """
        Create a hard commitment (specific time with exact timestamps).

        All datetime parameters should already be in UTC.

        Args:
            user_id: Owner of the commitment
            target_type: One of task, project, routine, session
            target_id: ID of the target entity
            timeframe_id: ID of the DAY timeframe this commitment belongs to
            due_at_utc: When the commitment is due (UTC)
            start_at_utc: Optional start time (UTC)
            status: Optional status (defaults to 'planned')
            notes: Optional notes
        """
        target_type = self._normalize_target_type(target_type)
        status = self._normalize_status(status)

        self._ensure_target_exists(user_id=user_id, target_type=target_type, target_id=int(target_id))
        self._ensure_timeframe_exists(user_id=user_id, timeframe_id=int(timeframe_id))

        existing = self.repo.find_by_unique(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=timeframe_id,
        )
        if existing is not None:
            raise CommitmentConflict("Hard commitment already exists for this target on that day.")

        return self.repo.create(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=timeframe_id,
            status=status,
            notes=notes,
            start_at_utc=start_at_utc,
            due_at_utc=due_at_utc,
        )


    def create_for_session(
            self,
            *,
            user_id: int,
            session_id: int,
            timeframe_id: int,
            start_at_utc: datetime,
            due_at_utc: datetime,
    ) -> Commitment:
        """
        Create a hard commitment for a session. Convenience method for auto-generation.

        Args:
            user_id: Owner of the commitment
            session_id: ID of the session
            timeframe_id: ID of the DAY timeframe
            start_at_utc: Session start time (UTC)
            due_at_utc: Session end time (UTC) - used as due time

        Returns:
            The created commitment
        """
        return self.create_hard(
            user_id=user_id,
            target_type="session",
            target_id=session_id,
            timeframe_id=timeframe_id,
            due_at_utc=due_at_utc,
            start_at_utc=start_at_utc,
            status="planned",
            notes=None,
        )

    def delete_for_target(
            self,
            *,
            user_id: int,
            target_type: str,
            target_id: int,
    ) -> bool:
        """
        Delete all commitments for a specific target.
        Used when deleting a session or other entity.

        Returns:
            True if any commitments were deleted
        """
        target_type = self._normalize_target_type(target_type)
        commitments = self.repo.list_for_target(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
        )

        deleted_any = False
        for commitment in commitments:
            self.repo.delete(commitment)
            deleted_any = True

        return deleted_any

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