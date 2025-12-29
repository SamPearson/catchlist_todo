from datetime import date, datetime, timedelta
from typing import Tuple

def get_next_day(input_date: date) -> date:
    """Get the next day's date."""
    return input_date + timedelta(days=1)

def get_previous_day(input_date: date) -> date:
    """Get the previous day's date."""
    return input_date - timedelta(days=1)

def format_date(input_date: date) -> str:
    """Format date as YYYY-MM-DD string."""
    return input_date.strftime('%Y-%m-%d')

def parse_date(date_str: str) -> date:
    """Parse YYYY-MM-DD string into date object."""
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def get_week_bounds(input_date: date) -> Tuple[date, date]:
    """Get the start and end dates of the week containing the input date."""
    year, week, _ = input_date.isocalendar()
    # Find Monday (start) of the week
    start = datetime.strptime(f'{year}-W{week:02d}-1', '%Y-W%W-%w').date()
    # End date is 6 days after start (Sunday)
    end = start + timedelta(days=6)
    return start, end

def get_week_sunday(input_date: date) -> date:
    """Get the Sunday that starts the week containing the input date.
    Treats Sunday as the first day of the week."""
    # weekday() returns 6 for Sunday, 0 for Monday, etc.
    days_since_sunday = input_date.weekday() + 1
    if days_since_sunday == 7:  # It's already Sunday
        return input_date
    return input_date - timedelta(days=days_since_sunday)

def get_next_week_sunday(input_date: date) -> date:
    """Get the Sunday that starts the next week"""
    current_sunday = get_week_sunday(input_date)
    return current_sunday + timedelta(days=7)

def get_previous_week_sunday(input_date: date) -> date:
    """Get the Sunday that starts the previous week"""
    current_sunday = get_week_sunday(input_date)
    return current_sunday - timedelta(days=7)

def get_season(input_date: date) -> str:
    """Get the season name for the given date."""
    month = input_date.month
    if 3 <= month <= 5:
        return 'spring'
    elif 6 <= month <= 8:
        return 'summer'
    elif 9 <= month <= 11:
        return 'fall'
    else:  # 12, 1, 2
        return 'winter'


def get_season_bounds(input_date: date) -> Tuple[date, date]:
    """Get the start and end dates of the season containing the input date."""
    year = input_date.year
    season = get_season(input_date)

    season_dates = {
        'winter': ((12, 1), (2, 28)),  # Special case spans year boundary
        'spring': ((3, 1), (5, 31)),
        'summer': ((6, 1), (8, 31)),
        'fall': ((9, 1), (11, 30))
    }

    start_month, start_day = season_dates[season][0]
    end_month, end_day = season_dates[season][1]

    # Handle winter spanning year boundary
    if season == 'winter' and input_date.month in (1, 2):
        start = date(year - 1, 12, 1)
        end = date(year, 2, 28)  # Note: doesn't handle leap years
    else:
        start = date(year, start_month, start_day)
        end = date(year, end_month, end_day)

    return start, end