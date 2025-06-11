from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..base import BaseReportEndpoint
from ..decorators import validate_date_format, handle_report_errors, validate_json
from .....config.models import DayReport, DayBlock

# Create blueprint for day reports
bp = Blueprint('day_reports', __name__)

# Create the endpoint handler
day_handler = BaseReportEndpoint('day', DayReport, DayBlock, '%Y-%m-%d')

@bp.route('/api/reports/day/<date_str>', methods=['GET'])
@jwt_required()
@validate_date_format('%Y-%m-%d')
@handle_report_errors
def get_day_report(date_str):
    """Get a day report for the specified date"""
    return day_handler.get_report(date_str)

@bp.route('/api/reports/day', methods=['POST'])
@jwt_required()
@validate_json(['date'])
@handle_report_errors
def create_day_report():
    """Create a new day report"""
    return day_handler.create_report()

@bp.route('/api/reports/day/<int:report_id>', methods=['PATCH'])
@jwt_required()
@validate_json()
@handle_report_errors
def update_day_report(report_id):
    """Update an existing day report"""
    return day_handler.update_report(report_id)

@bp.route('/api/reports/day/<int:report_id>', methods=['DELETE'])
@jwt_required()
@handle_report_errors
def delete_day_report(report_id):
    """Delete a day report"""
    return day_handler.delete_report(report_id)
