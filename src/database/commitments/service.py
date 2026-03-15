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
        include_targets: bool = False,
    ) -> list[Commitment]:
        """
        Flexible search for commitments with optional eager loading of targets.

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
            include_targets: If True, eagerly load and attach target entities

        Returns:
            List of commitments matching all provided filters.
            If include_targets=True, each commitment will have a .target attribute.
        """
        # Normalize target_type(s) if provided
        if target_type is not None:
            target_type = self._normalize_target_type(target_type)
        if target_types is not None:
            target_types = [self._normalize_target_type(tt) for tt in target_types]

        # Normalize status(es) if provided
        if status is not None:
            status = self._normalize_status(status)
        if statuses is not None:
            statuses = [self._normalize_status(s) for s in statuses]

        # Execute search
        commitments = self.repo.search(
            user_id=user_id,
            timeframe_id=timeframe_id,
            timeframe_ids=timeframe_ids,
            target_type=target_type,
            target_types=target_types,
            target_id=target_id,
            status=status,
            statuses=statuses,
            is_hard=is_hard,
            due_after=due_after,
            due_before=due_before,
        )

        # Eagerly load targets if requested
        if include_targets and commitments:
            self._attach_targets(commitments, user_id)

        return commitments

    def _attach_targets(self, commitments: list[Commitment], user_id: int) -> None:
        """
        Batch fetch and attach target entities to commitments.

        Groups commitments by target_type, fetches in batches, and attaches
        as a .target attribute on each commitment object.
        """
        from src.database.tasks.models import Task
        from src.database.projects.models import Project
        from src.database.routines.models import Routine
        from src.database.sessions.models import RoutineSession

        # Group commitments by target type
        by_type = {}
        for commitment in commitments:
            if commitment.target_type not in by_type:
                by_type[commitment.target_type] = []
            by_type[commitment.target_type].append(commitment)

        # Batch fetch each type
        for target_type, type_commitments in by_type.items():
            target_ids = [c.target_id for c in type_commitments]

            # Fetch targets based on type
            if target_type == "task":
                targets = (
                    self.session.query(Task)
                    .filter(Task.id.in_(target_ids), Task.user_id == user_id)
                    .all()
                )
            elif target_type == "project":
                targets = (
                    self.session.query(Project)
                    .filter(Project.id.in_(target_ids), Project.user_id == user_id)
                    .all()
                )
            elif target_type == "routine":
                targets = (
                    self.session.query(Routine)
                    .filter(Routine.id.in_(target_ids), Routine.user_id == user_id)
                    .all()
                )
            elif target_type == "session":
                targets = (
                    self.session.query(RoutineSession)
                    .filter(RoutineSession.id.in_(target_ids), RoutineSession.user_id == user_id)
                    .all()
                )
            else:
                targets = []

            # Create lookup dict
            target_map = {t.id: t for t in targets}

            # Attach targets to commitments
            for commitment in type_commitments:
                commitment.target = target_map.get(commitment.target_id)


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
            due_at_utc: datetime,
            timezone: str,
            start_at_utc: datetime | None = None,
            status: str | None = None,
            notes: str | None = None,
    ) -> Commitment:
        """
        Create a hard commitment (specific time with exact timestamps).

        The day timeframe is automatically derived from due_at_utc in the user's timezone.
        Projects cannot have hard commitments - use create_soft() instead.

        Args:
            user_id: Owner of the commitment
            target_type: One of task, project, routine, session
            target_id: ID of the target entity
            due_at_utc: When the commitment is due (UTC datetime)
            timezone: User's timezone (IANA string like "America/Chicago")
            start_at_utc: Optional start time (UTC datetime)
            status: Optional status (defaults to 'planned')
            notes: Optional notes

        Returns:
            The created hard commitment

        Raises:
            CommitmentValidationError: If target_type is invalid or project
            CommitmentTargetNotFound: If target doesn't exist or user doesn't own it
            CommitmentConflict: If commitment already exists for this target on this day
            ValueError: If timezone is invalid
        """
        target_type = self._normalize_target_type(target_type)

        # Projects can only have soft commitments
        if target_type == "project":
            raise CommitmentValidationError(
                "Projects can only have soft commitments. Use create_soft() instead."
            )

        status = self._normalize_status(status)

        self._ensure_target_exists(user_id=user_id, target_type=target_type, target_id=int(target_id))

        # Auto-derive the day timeframe from due_at_utc
        day_timeframe = self.timeframe_service.get_or_create_day_for_instant(
            user_id=user_id,
            instant_utc=due_at_utc,
            timezone=timezone,
        )

        # Check for duplicate commitment on this day
        existing = self.repo.find_by_unique(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=day_timeframe.id,
        )
        if existing is not None:
            raise CommitmentConflict(
                "This entity is already committed to this timeframe."
            )

        return self.repo.create(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            timeframe_id=day_timeframe.id,
            status=status,
            notes=notes,
            start_at_utc=start_at_utc,
            due_at_utc=due_at_utc,
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

    def update(
            self,
            *,
            user_id: int,
            commitment_id: int,
            status: str | None = None,
            notes: str | None = None,
            due_at_utc: datetime | None = None,
            start_at_utc: datetime | None = None,
    ) -> Commitment | None:
        """
        Update editable fields of a commitment.

        Whitelisted fields: status, notes, due_at_utc, start_at_utc
        Cannot change: target_type, target_id, timeframe_id

        Args:
            user_id: Owner of the commitment
            commitment_id: ID of the commitment to update
            status: New status (validated)
            notes: New notes text
            due_at_utc: New due time (UTC) - triggers timeframe recalculation for hard commitments
            start_at_utc: New start time (UTC)

        Returns:
            Updated commitment, or None if not found

        Raises:
            CommitmentValidationError: If status is invalid
        """
        c = self.get(user_id=user_id, commitment_id=commitment_id)
        if not c:
            return None

        # Build dict of fields to update
        updates = {}

        if status is not None:
            updates["status"] = self._normalize_status(status)

        if notes is not None:
            updates["notes"] = notes

        if start_at_utc is not None:
            updates["start_at_utc"] = start_at_utc

        if due_at_utc is not None:
            # For hard commitments, updating due_at might change the day
            # We need to recalculate the timeframe if this is a hard commitment
            if c.due_at_utc is not None:
                # This is a hard commitment - need to derive new day timeframe
                # But we don't have the timezone here...
                # Option 1: Require timezone parameter
                # Option 2: Store timezone on commitment
                # Option 3: Look up user's timezone
                # Let's go with Option 3 for now
                from src.database.users.user import User
                user = self.session.query(User).filter_by(id=user_id).first()
                if user and user.timezone:
                    new_day_timeframe = self.timeframe_service.get_or_create_day_for_instant(
                        user_id=user_id,
                        instant_utc=due_at_utc,
                        timezone=user.timezone,
                    )
                    updates["timeframe_id"] = new_day_timeframe.id

            updates["due_at_utc"] = due_at_utc

        # Apply updates
        if updates:
            return self.repo.update(c, **updates)

        return c

    def clear_start_at(self, *, user_id: int, commitment_id: int) -> Commitment | None:
        """
        Clear the start_at_utc field from a commitment.

        Args:
            user_id: Owner of the commitment
            commitment_id: ID of the commitment to update

        Returns:
            Updated commitment, or None if not found
        """
        c = self.get(user_id=user_id, commitment_id=commitment_id)
        if not c:
            return None
        return self.repo.update(c, start_at_utc=None)

    def clear_due_at(self, *, user_id: int, commitment_id: int) -> Commitment | None:
        """
        Clear the due_at_utc field from a commitment, converting it to a soft commitment.

        Note: This should rarely be needed as hard commitments typically shouldn't
        become soft commitments. Consider deleting and recreating instead.

        Args:
            user_id: Owner of the commitment
            commitment_id: ID of the commitment to update

        Returns:
            Updated commitment, or None if not found
        """
        c = self.get(user_id=user_id, commitment_id=commitment_id)
        if not c:
            return None
        return self.repo.update(c, due_at_utc=None)


    def list(self, *, user_id: int, timeframe_id: int | None = None) -> list[Commitment]:
        if timeframe_id is not None:
            return self.repo.list_for_timeframe(user_id=user_id, timeframe_id=timeframe_id)
        return self.repo.list_for_user(user_id=user_id)