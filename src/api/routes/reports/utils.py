from datetime import date, datetime, timedelta
from ....config.models import db
from ....config.models.reports import ReportGenerator

def get_season_from_date(input_date):
    """Determine season from date"""
    month = input_date.month
    if 3 <= month <= 5:
        return 'spring'
    elif 6 <= month <= 8:
        return 'summer'
    elif 9 <= month <= 11:
        return 'fall'
    else:  # 12, 1, 2
        return 'winter'

def generate_missing_reports(user_id):
    """Generate any missing reports for the user"""
    try:
        ReportGenerator.generate_missing_reports(user_id, db.session)
        return True, None
    except Exception as e:
        return False, str(e)

def parse_date_or_default(date_str, format_str='%Y-%m-%d', default=None):
    """Parse a date string or return default"""
    if not date_str:
        return default or date.today()

    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        raise ValueError(f"Invalid date format. Use {format_str}")
