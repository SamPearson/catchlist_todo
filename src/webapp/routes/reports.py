from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, date
from ...config.models.reports import DayReport, WeekReport, MonthReport, SeasonReport, YearReport
from ...config.models.time_blocks import DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from ...config.models.commitment import Commitment
from ...config.db_setup import db
from functools import wraps

reports_bp = Blueprint('reports', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # First try to get from headers
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.replace('Bearer ', '')
        # Then try to get from cookies
        if not token:
            token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
            
        # For now, we'll just check if the token exists
        # In a real app, you'd want to validate the token with your API
        return f(*args, **kwargs)
    return decorated

@reports_bp.route('/api/reports/day/<date_str>')
@token_required
def get_day_report(date_str):
    """Get a report for a specific day"""
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get or create the day block
    day_block = DayBlock.get_or_create(
        db=db.session,
        user_id=1,  # TODO: Get actual user_id from token
        year=report_date.year,
        month=report_date.month,
        day=report_date.day
    )
    
    # Generate the report
    report = DayReport(day_block, db.session)
    return jsonify(report.as_dict())

@reports_bp.route('/api/reports/week/<date_str>')
@token_required
def get_week_report(date_str):
    """Get a report for a specific week"""
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get or create the week block
    week_block = WeekBlock.get_or_create(
        db=db.session,
        user_id=1,  # TODO: Get actual user_id from token
        year=report_date.year,
        week_number=report_date.isocalendar()[1]
    )
    
    # Generate the report
    report = WeekReport(week_block, db.session)
    return jsonify(report.as_dict())

@reports_bp.route('/api/reports/month/<date_str>')
@token_required
def get_month_report(date_str):
    """Get a report for a specific month"""
    try:
        report_date = datetime.strptime(date_str, '%Y-%m').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM"}), 400
    
    # Get or create the month block
    month_block = MonthBlock.get_or_create(
        db=db.session,
        user_id=1,  # TODO: Get actual user_id from token
        year=report_date.year,
        month=report_date.month
    )
    
    # Generate the report
    report = MonthReport(month_block, db.session)
    return jsonify(report.as_dict())

@reports_bp.route('/api/reports/season/<year>/<season>')
@token_required
def get_season_report(year, season):
    """Get a report for a specific season"""
    try:
        year = int(year)
        if season not in ['Winter', 'Spring', 'Summer', 'Fall']:
            raise ValueError("Invalid season")
    except ValueError:
        return jsonify({"error": "Invalid year or season"}), 400
    
    # Get or create the season block
    season_block = SeasonBlock.get_or_create(
        db=db.session,
        user_id=1,  # TODO: Get actual user_id from token
        year=year,
        season_name=season
    )
    
    # Generate the report
    report = SeasonReport(season_block, db.session)
    return jsonify(report.as_dict())

@reports_bp.route('/api/reports/year/<year>')
@token_required
def get_year_report(year):
    """Get a report for a specific year"""
    try:
        year = int(year)
    except ValueError:
        return jsonify({"error": "Invalid year"}), 400
    
    # Get or create the year block
    year_block = YearBlock.get_or_create(
        db=db.session,
        user_id=1,  # TODO: Get actual user_id from token
        year=year
    )
    
    # Generate the report
    report = YearReport(year_block, db.session)
    return jsonify(report.as_dict())

@reports_bp.route('/api/reports/custom', methods=['POST'])
@token_required
def get_custom_report():
    """Get a report for a custom date range"""
    data = request.get_json()
    if not data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({"error": "Missing start_date or end_date"}), 400
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Create a custom time block
    time_block = TimeBlock(
        user_id=1,  # TODO: Get actual user_id from token
        start_date=start_date,
        end_date=end_date,
        block_type='custom'
    )
    
    # Generate the report
    report = Report(time_block, db.session)
    return jsonify(report.as_dict())

@reports_bp.route('/api/reports/demo/<report_type>')
@token_required
def get_demo_report(report_type):
    """Get a demo report of the specified type"""
    if not current_app.config['SHOW_DEMO']:
        return jsonify({"error": "Demo reports are not enabled"}), 403
    
    # Create demo data based on report type
    today = date.today()
    
    if report_type == 'day':
        time_block = DayBlock(
            user_id=1,  # TODO: Get actual user_id from token
            year=today.year,
            month=today.month,
            day=today.day,
            sleep_hours=7.5,
            mood='Good',
            rpe=6
        )
    elif report_type == 'week':
        time_block = WeekBlock(
            user_id=1,  # TODO: Get actual user_id from token
            year=today.year,
            week_number=today.isocalendar()[1],
            weekly_aim='Complete project milestone',
            weekly_notes='Focus on core features'
        )
    elif report_type == 'month':
        time_block = MonthBlock(
            user_id=1,  # TODO: Get actual user_id from token
            year=today.year,
            month=today.month,
            theme='Productivity Boost'
        )
    elif report_type == 'season':
        # Determine current season
        month = today.month
        if month in [12, 1, 2]:
            season = 'Winter'
        elif month in [3, 4, 5]:
            season = 'Spring'
        elif month in [6, 7, 8]:
            season = 'Summer'
        else:
            season = 'Fall'
        
        time_block = SeasonBlock(
            user_id=1,  # TODO: Get actual user_id from token
            year=today.year,
            season_name=season,
            aim='Improve work-life balance'
        )
    elif report_type == 'year':
        time_block = YearBlock(
            user_id=1,  # TODO: Get actual user_id from token
            year=today.year,
            theme='Personal Growth'
        )
    else:
        return jsonify({"error": "Invalid report type"}), 400
    
    # Add some demo commitments
    commitments = [
        Commitment(
            user_id=1,  # TODO: Get actual user_id from token
            title="Complete project documentation",
            completed=True,
            rpe=7
        ),
        Commitment(
            user_id=1,  # TODO: Get actual user_id from token
            title="Review pull requests",
            completed=True,
            rpe=5
        ),
        Commitment(
            user_id=1,  # TODO: Get actual user_id from token
            title="Team meeting",
            completed=False,
            rpe=None
        ),
        Commitment(
            user_id=1,  # TODO: Get actual user_id from token
            title="Update dependencies",
            completed=False,
            rpe=None
        )
    ]
    
    # Create and return the report
    report_class = {
        'day': DayReport,
        'week': WeekReport,
        'month': MonthReport,
        'season': SeasonReport,
        'year': YearReport
    }[report_type]
    
    report = report_class(time_block, db.session)
    report._commitments = commitments  # Override the commitments property
    
    return jsonify(report.as_dict()) 