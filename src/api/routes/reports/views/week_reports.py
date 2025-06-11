from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..base import BaseReportEndpoint
from ..decorators import validate_date_format, handle_report_errors, validate_json
from .....config.models import WeekReport, WeekBlock

# Create blueprint for week reports
bp = Blueprint('week_reports', __name__)

# Create the endpoint handler
week_handler = BaseReportEndpoint('week', WeekReport, WeekBlock, '%Y-%m-%d')

@bp.route('/api/reports/week/<date_str>', methods=['GET'])
@jwt_required()
@validate_date_format('%Y-%m-%d')
@handle_report_errors
def get_week_report(date_str):
    """Get a week report containing the specified date"""
    return week_handler.get_report(date_str)

@bp.route('/api/reports/week', methods=['POST'])
@jwt_required()
@validate_json(['date'])
@handle_report_errors
def create_week_report():
    """Create a new week report"""
    return week_handler.create_report()

@bp.route('/api/reports/week/<int:report_id>', methods=['PATCH'])
@jwt_required()
@validate_json()
@handle_report_errors
def update_week_report(report_id):
    """Update an existing week report"""
    return week_handler.update_report(report_id)

@bp.route('/api/reports/week/<int:report_id>', methods=['DELETE'])
@jwt_required()
@handle_report_errors
def delete_week_report(report_id):
    """Delete a week report"""
    return week_handler.delete_report(report_id)
