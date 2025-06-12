from datetime import date, datetime, timedelta
from typing import Tuple


def get_week_bounds(input_date: date) -> Tuple[date, date]:
    """Get the start and end dates of the week containing the input date."""
    year, week, _ = input_date.isocalendar()
    # Find Monday (start) of the week
    start = datetime.strptime(f'{year}-W{week:02d}-1', '%Y-W%W-%w').date()
    # End date is 6 days after start (Sunday)
    end = start + timedelta(days=6)
    return start, end


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