from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..base import BaseReportEndpoint
from ..decorators import handle_report_errors, validate_json
from ..utils import get_season_from_date, parse_date_or_default
from .....config.models import SeasonReport, SeasonBlock, db
from .....config.models.reports import ReportGenerator
from ....utils.helpers import get_current_user_id

# Create blueprint for season reports
bp = Blueprint('season_reports', __name__)

# Create the endpoint handler
season_handler = BaseReportEndpoint('season', SeasonReport, SeasonBlock)

@bp.route('/api/reports/season/<int:year>/<season_name>', methods=['GET'])
@jwt_required()
@handle_report_errors
def get_season_report(year, season_name):
    """Get a season report for the specified year and season"""
    user_id = get_current_user_id()

    try:
        # Validate season name
        season_name = season_name.lower()
        if season_name not in ['winter', 'spring', 'summer', 'fall']:
            return jsonify({"error": "Invalid season name. Use winter, spring, summer, or fall"}), 400

        # Get or create the season block
        season_block = SeasonBlock.get_or_create(db.session, user_id, year, season_name)

        # Look for an existing report
        report = SeasonReport.query.filter_by(
            user_id=user_id,
            start_date=season_block.start_date,
            end_date=season_block.end_date
        ).first()

        # If no report exists, create one
        if not report:
            report = ReportGenerator.create_season_report_model(user_id, season_block, db.session)

        return jsonify(report.as_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/reports/season', methods=['POST'])
@jwt_required()
@validate_json(['year', 'season'])
@handle_report_errors
def create_season_report():
    """Create a new season report"""
    user_id = get_current_user_id()
    data = request.get_json()

    try:
        year = int(data['year'])
        season_name = data['season'].lower()

        if season_name not in ['winter', 'spring', 'summer', 'fall']:
            return jsonify({"error": "Invalid season name. Use winter, spring, summer, or fall"}), 400

        # Get or create the season block
        season_block = SeasonBlock.get_or_create(db.session, user_id, year, season_name)

        # Check if report already exists
        existing_report = SeasonReport.query.filter_by(
            user_id=user_id,
            start_date=season_block.start_date,
            end_date=season_block.end_date
        ).first()

        if existing_report:
            return jsonify({"error": "Report already exists for this season"}), 409

        # Create the report
        report = ReportGenerator.create_season_report_model(user_id, season_block, db.session)

        return jsonify(report.as_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/reports/season/<int:report_id>', methods=['PATCH'])
@jwt_required()
@validate_json()
@handle_report_errors
def update_season_report(report_id):
    """Update an existing season report"""
    return season_handler.update_report(report_id)

@bp.route('/api/reports/season/<int:report_id>', methods=['DELETE'])
@jwt_required()
@handle_report_errors
def delete_season_report(report_id):
    """Delete a season report"""
    return season_handler.delete_report(report_id)
