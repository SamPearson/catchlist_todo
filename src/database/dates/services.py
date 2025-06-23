# dates/service.py
from datetime import date, datetime, timedelta
from typing import Literal, Optional

class DateService:

    @staticmethod
    def get_week_start(input_date: date) -> date:
        """Get the start date (Monday) of the week containing the given date"""
        return input_date - timedelta(days=input_date.weekday())

    @staticmethod
    def get_season_from_date(input_date: date) -> Literal['spring', 'summer', 'fall', 'winter']:
        """Determine season from date"""
        month = input_date.month
        if 3 <= month <= 5:
            return 'spring'
        elif 6 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 11:
            return 'fall'
        else:
            return 'winter'

    @staticmethod
    def parse_date(date_str: str, format_str: str = '%Y-%m-%d', default: Optional[date] = None) -> date:
        """Parse a date string or return default"""
        if not date_str:
            return default or date.today()

        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            raise ValueError(f"Invalid date format. Use {format_str}")