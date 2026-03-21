from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from sqlalchemy.orm import Session

from src.database.timeframes.repository import TimeframeRepo
from src.database.timeframes.models import Timeframe
from src.database.base.exceptions import ValidationError


@dataclass(frozen=True)
class TimeframeBounds:
    start_utc: datetime
    end_utc: datetime
    label: str | None = None


@dataclass(frozen=True)
class TimeframeValidationError(ValidationError):
    message: str


@dataclass(frozen=True)
class UnsupportedTimeframeKind(TimeframeValidationError):
    kind: str

    def __post_init__(self):
        if not self.message:
            object.__setattr__(self, "message", f"Unsupported timeframe kind: {self.kind}")


@dataclass(frozen=True)
class InvalidTimezone(TimeframeValidationError):
    tz: str

    def __post_init__(self):
        if not self.message:
            object.__setattr__(self, "message", f"Invalid timezone: {self.tz}")


SUPPORTED_KINDS = {"day", "week", "month", "season", "year"}


def validate_kind(kind: str) -> str | None:
    """
    Validate that kind is a supported timeframe kind.
    
    Args:
        kind: The timeframe kind to validate
        
    Returns:
        None if valid, or error message string if invalid
    """
    kind = (kind or "").strip().lower()
    if kind not in SUPPORTED_KINDS:
        allowed = ", ".join(sorted(SUPPORTED_KINDS))
        return f"Invalid timeframe kind '{kind}'. Allowed kinds: {allowed}."
    return None


class TimeframeService:
    def __init__(self, session: Session):
        self.repo = TimeframeRepo(session=session)

    def get_or_create_for_date(
            self,
            *,
            user_id: int,
            kind: str,
            local_date: date,
            timezone: str,
    ) -> Timeframe:
        """
        Get or create a timeframe of the specified kind containing the given date.

        This derives the appropriate timeframe boundaries based on kind and date,
        then uses get-or-create semantics to return the timeframe.

        Args:
            user_id: The user ID
            kind: The timeframe kind (day, week, month, season, year)
            local_date: The date (in the user's timezone) to find/create a timeframe for
            timezone: User's timezone (IANA string like "America/Chicago")

        Returns:
            The timeframe containing this date

        Raises:
            UnsupportedTimeframeKind: If kind is not supported
            ValueError: If timezone is invalid or date computation fails
        """
        from src.utils.timezone import compute_timeframe_bounds

        kind_error = validate_kind(kind)
        if kind_error:
            raise UnsupportedTimeframeKind(kind=kind, message=kind_error)

        # Compute UTC bounds for this timeframe
        start_utc, end_utc, label = compute_timeframe_bounds(kind, local_date, timezone)

        # Get or create the timeframe with these bounds
        return self.get_or_create_for_bounds(
            user_id=user_id,
            kind=kind,
            start_utc=start_utc,
            end_utc=end_utc,
            label=label,
        )

    def get_or_create_day_for_instant(
            self,
            *,
            user_id: int,
            instant_utc: datetime,
            timezone: str,
    ) -> Timeframe:
        """
        Get or create the DAY timeframe containing a specific UTC instant.

        This is a convenience method specifically for hard commitments, which need
        to derive their day timeframe from a due_at_utc timestamp.

        Args:
            user_id: The user ID
            instant_utc: A UTC datetime that falls within the desired day
            timezone: User's timezone to determine which day this instant belongs to

        Returns:
            The day timeframe containing this instant

        Raises:
            ValueError: If timezone is invalid
        """
        from zoneinfo import ZoneInfo

        # Convert UTC instant to local date in user's timezone
        zone = ZoneInfo(timezone)
        local_datetime = instant_utc.astimezone(zone)
        local_date = local_datetime.date()

        # Get or create the day timeframe for this date
        return self.get_or_create_for_date(
            user_id=user_id,
            kind="day",
            local_date=local_date,
            timezone=timezone,
        )

    def get_or_create_for_bounds(
        self,
        *,
        user_id: int,
        kind: str,
        start_utc: datetime,
        end_utc: datetime,
        label: str | None = None,
    ) -> Timeframe:
        """
        Get or create a timeframe with pre-computed UTC bounds.
        
        The caller is responsible for converting local dates to UTC bounds
        based on timezone context.
        
        Args:
            user_id: The user ID
            kind: The timeframe kind (day, week, month, etc.)
            start_utc: UTC start datetime (inclusive)
            end_utc: UTC end datetime (exclusive)
            label: Optional human-readable label
            
        Returns:
            The timeframe
            
        Raises:
            UnsupportedTimeframeKind: If kind is not supported
        """
        kind_error = validate_kind(kind)
        if kind_error:
            raise UnsupportedTimeframeKind(kind=kind, message=kind_error)

        existing = self.repo.find_exact(
            user_id=user_id,
            kind=kind,
            start_at_utc=start_utc,
        )
        if existing is not None:
            return existing

        return self.repo.create(
            user_id=user_id,
            kind=kind,
            start_at_utc=start_utc,
            end_at_utc=end_utc,
            label=label,
        )

    def get_or_create_for_bounds_with_flag(
        self,
        *,
        user_id: int,
        kind: str,
        start_utc: datetime,
        end_utc: datetime,
        label: str | None = None,
    ) -> tuple[Timeframe, bool]:
        """Same as get_or_create_for_bounds but returns a flag indicating creation."""
        kind_error = validate_kind(kind)
        if kind_error:
            raise UnsupportedTimeframeKind(kind=kind, message=kind_error)

        existing = self.repo.find_exact(
            user_id=user_id,
            kind=kind,
            start_at_utc=start_utc,
        )
        if existing is not None:
            return existing, False

        created = self.repo.create(
            user_id=user_id,
            kind=kind,
            start_at_utc=start_utc,
            end_at_utc=end_utc,
            label=label,
        )
        return created, True

    def get_timeframe(self, timeframe_id: int, user_id: int) -> Timeframe | None:
        """Retrieve a specific timeframe by ID and user_id"""
        return self.repo.get(timeframe_id, user_id=user_id)

