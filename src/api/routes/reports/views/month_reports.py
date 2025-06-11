from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..base import BaseReportEndpoint
from ..decorators import validate_date_format, handle_report_errors, validate_json
from .....config.models import MonthReport, MonthBlock

# Create blueprint for month reports
bp = Blueprint('month_reports', __name__)

# Create the endpoint handler
month_handler = BaseReportEndpoint('month', MonthReport, MonthBlock, '%Y-%m-%d')

@bp.route('/api/reports/month/<date_str>', methods=['GET'])
@jwt_required()
@validate_date_format('%Y-%m-%d')
@handle_report_errors
def get_month_report(date_str):
    """Get a month report for the specified month"""
    return month_handler.get_report(date_str)

@bp.route('/api/reports/month', methods=['POST'])
@jwt_required()
@validate_json(['date'])
@handle_report_errors
def create_month_report():
    """Create a new month report"""
    return month_handler.create_report()

@bp.route('/api/reports/month/<int:report_id>', methods=['PATCH'])
@jwt_required()
@validate_json()
@handle_report_errors
def update_month_report(report_id):
    """Update an existing month report"""
    return month_handler.update_report(report_id)

@bp.route('/api/reports/month/<int:report_id>', methods=['DELETE'])
@jwt_required()
@handle_report_errors
def delete_month_report(report_id):
    """Delete a month report"""
    return month_handler.delete_report(report_id)
