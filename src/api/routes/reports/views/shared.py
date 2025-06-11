from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ....utils.helpers import get_current_user_id
from ...reports import reports_bp
from .....config.models import db
from .....config.models.reports import ReportGenerator



@reports_bp.route('/api/reports/demo/<report_type>', methods=['GET'])
@jwt_required()
def get_demo_report(report_type):
    """Get a demo report of the specified type"""
    from flask import current_app
    from datetime import date
    from .....config.models import (
        Commitment, DayBlock, WeekBlock, MonthBlock, 
        SeasonBlock, YearBlock, DayReport, WeekReport,
        MonthReport, SeasonReport, YearReport
    )

    if not current_app.config.get('SHOW_DEMO', False):
        return jsonify({"error": "Demo reports are not enabled"}), 403

    # Create demo data based on report type
    today = date.today()
    user_id = get_current_user_id()

    if report_type == 'day':
        time_block = DayBlock(
            user_id=user_id,
            year=today.year,
            month=today.month,
            day=today.day,
            sleep_hours=7.5,
            mood='Good',
            rpe=6
        )
        report_class = DayReport
    elif report_type == 'week':
        time_block = WeekBlock(
            user_id=user_id,
            year=today.year,
            week_number=today.isocalendar()[1],
            weekly_aim='Complete project milestone',
            weekly_notes='Focus on core features'
        )
        report_class = WeekReport
    elif report_type == 'month':
        time_block = MonthBlock(
            user_id=user_id,
            year=today.year,
            month=today.month,
            theme='Productivity Boost'
        )
        report_class = MonthReport
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
            user_id=user_id,
            year=today.year,
            season_name=season,
            aim='Improve work-life balance'
        )
        report_class = SeasonReport
    elif report_type == 'year':
        time_block = YearBlock(
            user_id=user_id,
            year=today.year,
            theme='Personal Growth'
        )
        report_class = YearReport
    else:
        return jsonify({"error": "Invalid report type"}), 400

    # Add some demo commitments
    commitments = [
        Commitment(
            user_id=user_id,
            title="Complete project documentation",
            completed=True,
            rpe=7
        ),
        Commitment(
            user_id=user_id,
            title="Review pull requests",
            completed=True,
            rpe=5
        ),
        Commitment(
            user_id=user_id,
            title="Team meeting",
            completed=False,
            rpe=None
        ),
        Commitment(
            user_id=user_id,
            title="Update dependencies",
            completed=False,
            rpe=None
        )
    ]

    # Create and return the report
    report = report_class(time_block, db.session)
    report._commitments = commitments  # Override the commitments property

    return jsonify(report.as_dict())

@reports_bp.route('/api/reports/custom', methods=['POST'])
@jwt_required()
def get_custom_report():
    """Get a report for a custom date range"""
    from .....config.models import TimeBlock, BaseReport

    user_id = get_current_user_id()
    data = request.get_json()

    if not data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({"error": "Missing start_date or end_date"}), 400

    try:
        from datetime import datetime
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        # Create a custom time block
        time_block = TimeBlock(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            block_type='custom'
        )

        # Generate the report
        report = BaseReport(time_block, db.session)
        return jsonify(report.as_dict())
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
