from datetime import datetime, timedelta
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.reports.models import WeekReport
from src.database.reports.service import ReportService
from src.database.reports.repositories import ReportRepository
from src.config.models import db

# Create a single instance of the service
report_service = ReportService(ReportRepository(db.session))


@jwt_required()
def get_report(date):
    """Get a week report for the specified date"""
    user_id = get_jwt_identity()
    report_date = datetime.strptime(date, '%Y-%m-%d').date()
    report = report_service.get_week_report(user_id, date=report_date)
    return jsonify(report.as_dict()) if report else ('', 404)



@jwt_required()
def list_reports():
    """List all week reports for user"""
    user_id = get_jwt_identity()
    reports = report_service.list_reports(WeekReport, user_id=user_id)
    return jsonify([r.as_dict() for r in reports])


@jwt_required()
def create_report():
    """Create a new week report"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Handle start date
    start_date = datetime.strptime(data.pop('date'), '%Y-%m-%d').date()

    # Create report - note that end_date is calculated inside create_week_report
    report = report_service.create_week_report(user_id, start_date, data)
    return jsonify(report.as_dict()), 201


@jwt_required()
def update_report(report_id):
    """Update a week report"""
    user_id = get_jwt_identity()
    report = report_service.get_week_report(id=report_id, user_id=user_id)
    if not report:
        return ('', 404)

    data = request.get_json()
    updated = report_service.update_report(report, data)
    return jsonify(updated.as_dict())


@jwt_required()
def delete_report(report_id):
    """Delete a week report"""
    user_id = get_jwt_identity()
    report = report_service.get_week_report(id=report_id, user_id=user_id)
    if not report:
        return ('', 404)

    report_service.delete_report(report)
    return ('', 204)