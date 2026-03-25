"""
Timezone utilities for handling datetime conversions.

Simple, explicit functions to convert between UTC and user timezones.
"""

from datetime import datetime, time, date, timedelta
from typing import Optional
from zoneinfo import ZoneInfo
import logging


def to_utc(dt: datetime, from_timezone: str) -> datetime:
    """
    Convert a datetime from a user timezone to UTC.

    Args:
        dt: The datetime to convert (assumed to be in from_timezone)
        from_timezone: The source timezone (e.g., 'America/Chicago')

    Returns:
        Timezone-aware UTC datetime
    """
    # If the datetime already has timezone info, clear it first
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    # Apply the source timezone
    try:
        source_tz = ZoneInfo(from_timezone)
        dt_with_tz = dt.replace(tzinfo=source_tz)

        # Convert to UTC
        utc_tz = ZoneInfo("UTC")
        utc_dt = dt_with_tz.astimezone(utc_tz)

        return utc_dt
    except Exception as e:
        logging.error(f"Error converting to UTC: {str(e)}")
        # Fallback - assume it's already UTC
        return dt.replace(tzinfo=ZoneInfo("UTC"))


def from_utc(dt: datetime, to_timezone: str) -> datetime:
    """
    Convert a datetime from UTC to a user timezone.

    Args:
        dt: The datetime to convert (assumed to be in UTC)
        to_timezone: The target timezone (e.g., 'America/Chicago')

    Returns:
        Timezone-aware datetime in the target timezone
    """
    # If the datetime already has timezone info, clear it first
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    # Apply UTC timezone
    utc_tz = ZoneInfo("UTC")
    dt_with_tz = dt.replace(tzinfo=utc_tz)

    # Convert to target timezone
    try:
        target_tz = ZoneInfo(to_timezone)
        local_dt = dt_with_tz.astimezone(target_tz)
        return local_dt
    except Exception as e:
        logging.error(f"Error converting from UTC: {str(e)}")
        # Return UTC time as fallback
        return dt_with_tz


def validate_timezone(tz: str) -> Optional[str]:
    """
    Validate a timezone string.
    
    Args:
        tz: The timezone to validate
        
    Returns:
        None if valid, error message string if invalid
    """
    try:
        ZoneInfo(tz)
        return None
    except Exception:
        return f"Invalid timezone '{tz}'. Expected an IANA timezone like 'America/Chicago'."


def utc_to_local_date(utc_dt: datetime, user_tz: str) -> date:
    """
    Convert a UTC datetime to the user's local date.
    
    Args:
        utc_dt: The UTC datetime
        user_tz: The user's timezone
        
    Returns:
        The local date
        
    Raises:
        ValueError: If timezone is invalid
    """
    local_dt = from_utc(utc_dt, user_tz)
    return local_dt.date()


def parse_dt(date_string: str, timezone: Optional[str] = None) -> datetime:
    """
    Parse a string to a datetime object.

    Args:
        date_string: ISO format date string
        timezone: Optional timezone to apply if string has no timezone info

    Returns:
        Timezone-aware datetime
    """
    # Handle different date formats
    if 'T' in date_string:
        # Full ISO datetime
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            # Handle older Python versions or non-standard formats
            from dateutil.parser import parse as dateutil_parse
            dt = dateutil_parse(date_string)
    else:
        # Date only - assume midnight
        year, month, day = date_string.split('-')
        dt = datetime(int(year), int(month), int(day), 0, 0, 0)

    # If the datetime has timezone info, return as is
    if dt.tzinfo is not None:
        return dt

    # Otherwise, apply the specified timezone or default to UTC
    if timezone:
        return dt.replace(tzinfo=ZoneInfo(timezone))
    else:
        return dt.replace(tzinfo=ZoneInfo("UTC"))


def format_dt(dt: datetime, format_str: Optional[str] = None) -> str:
    """
    Format a datetime object to string.

    Args:
        dt: Datetime to format
        format_str: Optional strftime format string

    Returns:
        Formatted datetime string
    """
    if format_str:
        return dt.strftime(format_str)
    else:
        # Default to ISO format
        return dt.isoformat()


def to_utc_datetime(dt: datetime, from_timezone: str) -> datetime:
    """Convert a full datetime from user timezone to UTC"""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    source_tz = ZoneInfo(from_timezone)
    dt_with_tz = dt.replace(tzinfo=source_tz)
    return dt_with_tz.astimezone(ZoneInfo("UTC"))

def from_utc_datetime(dt: datetime, to_timezone: str) -> datetime:
    """Convert a full datetime from UTC to user timezone"""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    dt_with_tz = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt_with_tz.astimezone(ZoneInfo(to_timezone))

def format_time_of_day(t: time) -> str:
    """Format a time object to HH:MM string"""
    return t.strftime("%H:%M")

def parse_time_of_day(time_str: str) -> time:
    """Parse HH:MM string to time object"""
    hours, minutes = map(int, time_str.split(':'))
    return time(hours, minutes)

def localize_dict(data: dict, timezone: str) -> dict:
    """
    Convert timestamps in a dictionary based on their type.
    
    Datetime fields: created_at, updated_at (convert from UTC)
    Time-of-day fields: start_time, end_time (pass through as HH:MM)
    """
    if not data:
        return data

    result = data.copy()
    
    # Full datetime fields (UTC conversion needed)
    datetime_fields = ['created_at', 'updated_at']
    for field in datetime_fields:
        if field in result and result[field]:
            dt = datetime.fromisoformat(result[field].replace('Z', '+00:00'))
            local_dt = from_utc_datetime(dt, timezone)
            result[field] = local_dt.isoformat()
    
    # Time-of-day fields (no conversion needed, already in HH:MM)
    time_fields = ['start_time', 'end_time']
    for field in time_fields:
        if field in result and result[field]:
            # Validate HH:MM format but don't convert
            try:
                parse_time_of_day(result[field])
            except ValueError:
                # If it's not in HH:MM format, set to None
                result[field] = None

    return result


def compute_timeframe_bounds(
        kind: str,
        local_day: date,
        user_tz: str,
) -> tuple[datetime, datetime, str]:
    """
    Compute UTC bounds for a timeframe given a local date.

    Args:
        kind: Timeframe kind ('day', 'week', 'month', 'season', 'year')
        local_day: The local calendar date
        user_tz: The user's timezone (e.g., 'America/Chicago')

    Returns:
        Tuple of (start_utc, end_utc, label)

    Raises:
        ValueError: If timezone or kind is invalid
    """
    try:
        tz = ZoneInfo(user_tz)
    except Exception:
        raise ValueError(f"Invalid timezone: {user_tz}")

    utc = ZoneInfo("UTC")

    if kind == "day":
        start_local = datetime.combine(local_day, time.min, tzinfo=tz)
        end_local = start_local + timedelta(days=1)
        label = local_day.isoformat()

    elif kind == "week":
        # Sunday start
        days_since_sunday = (local_day.weekday() + 1) % 7
        start_of_week = local_day - timedelta(days=days_since_sunday)

        start_local = datetime.combine(start_of_week, time.min, tzinfo=tz)
        end_local = start_local + timedelta(days=7)

        # Optional: adjust label (ISO week no longer matches Sunday-based weeks)
        label = start_of_week.strftime("%Y-W%U")  # %U = week number, Sunday start


    elif kind == "month":
        start_local = datetime.combine(local_day.replace(day=1), time.min, tzinfo=tz)
        if local_day.month == 12:
            next_month = date(local_day.year + 1, 1, 1)
        else:
            next_month = date(local_day.year, local_day.month + 1, 1)
        end_local = datetime.combine(next_month, time.min, tzinfo=tz)
        label = local_day.strftime("%B %Y")

    elif kind == "season":
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

    elif kind == "year":
        start_local = datetime.combine(date(local_day.year, 1, 1), time.min, tzinfo=tz)
        end_local = datetime.combine(date(local_day.year + 1, 1, 1), time.min, tzinfo=tz)
        label = f"{local_day.year:04d}"

    else:
        raise ValueError(f"Unsupported timeframe kind: {kind}")

    return (
        start_local.astimezone(utc),
        end_local.astimezone(utc),
        label,
    )