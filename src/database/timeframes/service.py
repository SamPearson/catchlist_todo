from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

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


class TimeframeService:
    KIND_DAY = "day"
    KIND_WEEK = "week"
    KIND_MONTH = "month"
    KIND_SEASON = "season"
    KIND_YEAR = "year"

    def __init__(self, session: Session):
        self.repo = TimeframeRepo(session=session)

    def get_or_create_for_local_date(
        self,
        *,
        user_id: int,
        kind: str,
        local_day: date,
        user_tz: str,
    ) -> Timeframe:
        bounds = self.compute_bounds_for_local_date(kind=kind, local_day=local_day, user_tz=user_tz)

        existing = self.repo.find_exact(
            user_id=user_id,
            kind=kind,
            start_at_utc=bounds.start_utc,
        )
        if existing is not None:
            return existing

        return self.repo.create(
            user_id=user_id,
            kind=kind,
            start_at_utc=bounds.start_utc,
            end_at_utc=bounds.end_utc,
            label=bounds.label,
        )

    def compute_bounds_for_local_date(
        self,
        *,
        kind: str,
        local_day: date,
        user_tz: str,
    ) -> TimeframeBounds:
        try:
            tz = ZoneInfo(user_tz)
        except Exception:
            raise InvalidTimezone(message="", tz=user_tz)

        utc = ZoneInfo("UTC")

        if kind == self.KIND_DAY:
            start_local = datetime.combine(local_day, time.min, tzinfo=tz)
            end_local = start_local + timedelta(days=1)
            label = local_day.isoformat()

        elif kind == self.KIND_WEEK:
            # ISO week: Monday start
            start_of_week = local_day - timedelta(days=local_day.weekday())
            start_local = datetime.combine(start_of_week, time.min, tzinfo=tz)
            end_local = start_local + timedelta(days=7)
            iso_year, iso_week, _ = local_day.isocalendar()
            label = f"{iso_year}-W{iso_week:02d}"

        elif kind == self.KIND_MONTH:
            start_local = datetime.combine(local_day.replace(day=1), time.min, tzinfo=tz)
            if local_day.month == 12:
                next_month = date(local_day.year + 1, 1, 1)
            else:
                next_month = date(local_day.year, local_day.month + 1, 1)
            end_local = datetime.combine(next_month, time.min, tzinfo=tz)
            label = f"{local_day.year:04d}-{local_day.month:02d}"

        elif kind == self.KIND_SEASON:
            # Meteorological seasons:
            # Winter: Dec/Jan/Feb
            # Spring: Mar/Apr/May
            # Summer: Jun/Jul/Aug
            # Autumn: Sep/Oct/Nov
            m = local_day.month
            if m in (12, 1, 2):
                season_name = "Winter"
                start_year = local_day.year if m == 12 else local_day.year - 1
                start_month = 12
                end_year = start_year + 1
                end_month = 3
            elif m in (3, 4, 5):
                season_name = "Spring"
                start_year = local_day.year
                start_month = 3
                end_year = local_day.year
                end_month = 6
            elif m in (6, 7, 8):
                season_name = "Summer"
                start_year = local_day.year
                start_month = 6
                end_year = local_day.year
                end_month = 9
            else:
                season_name = "Autumn"
                start_year = local_day.year
                start_month = 9
                end_year = local_day.year
                end_month = 12

            start_local = datetime.combine(date(start_year, start_month, 1), time.min, tzinfo=tz)
            end_local = datetime.combine(date(end_year, end_month, 1), time.min, tzinfo=tz)
            label = f"{season_name} {start_year:04d}"

        elif kind == self.KIND_YEAR:
            start_local = datetime.combine(date(local_day.year, 1, 1), time.min, tzinfo=tz)
            end_local = datetime.combine(date(local_day.year + 1, 1, 1), time.min, tzinfo=tz)
            label = f"{local_day.year:04d}"

        else:
            raise UnsupportedTimeframeKind(message="", kind=kind)

        return TimeframeBounds(
            start_utc=start_local.astimezone(utc),
            end_utc=end_local.astimezone(utc),
            label=label,
        )

    def get_timeframe(self, timeframe_id: int, user_id: int) -> Timeframe | None:
        """Retrieve a specific timeframe by ID and user_id"""
        return self.repo.get(timeframe_id, user_id=user_id)

    def delete_timeframe(self, timeframe_id: int, user_id: int) -> bool:
        """Delete a timeframe ensuring ownership"""
        tf = self.get_timeframe(timeframe_id, user_id)
        if not tf:
            return False
        return self.repo.delete(tf)