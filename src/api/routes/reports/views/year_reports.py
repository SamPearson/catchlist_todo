from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..base import BaseReportEndpoint
from ..decorators import handle_report_errors, validate_json
from .....config.models import YearReport, YearBlock

# Create blueprint for year reports
bp = Blueprint('year_reports', __name__)

# Create the endpoint handler
year_handler = BaseReportEndpoint('year', YearReport, YearBlock)

@bp.route('/api/reports/year/<int:year>', methods=['GET'])
@jwt_required()
@handle_report_errors
def get_year_report(year):
    """Get a year report for the specified year"""
    from datetime import date
    # Convert year to a date for the handler
    date_str = f"{year}-01-01"
    return year_handler.get_report(date_str)

@bp.route('/api/reports/year', methods=['POST'])
@jwt_required()
@validate_json(['year'])
@handle_report_errors
def create_year_report():
    """Create a new year report"""
    return year_handler.create_report()

@bp.route('/api/reports/year/<int:report_id>', methods=['PATCH'])
@jwt_required()
@validate_json()
@handle_report_errors
def update_year_report(report_id):
    """Update an existing year report"""
    return year_handler.update_report(report_id)

@bp.route('/api/reports/year/<int:report_id>', methods=['DELETE'])
@jwt_required()
@handle_report_errors
def delete_year_report(report_id):
    """Delete a year report"""
    return year_handler.delete_report(report_id)
