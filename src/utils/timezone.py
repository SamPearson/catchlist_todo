"""
Timezone utilities for handling datetime conversions.

Simple, explicit functions to convert between UTC and user timezones.
"""

from datetime import datetime, time
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