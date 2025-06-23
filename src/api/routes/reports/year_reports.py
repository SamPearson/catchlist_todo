from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.reports.models import YearReport
from src.database.reports.service import ReportService
from src.database.reports.repositories import ReportRepository
from src.config.models import db

# Create a single instance of the service
report_service = ReportService(ReportRepository(db.session))


@jwt_required()
def get_report(date):
    """Get a year report for the specified date"""
    user_id = get_jwt_identity()
    report_date = datetime.strptime(date, '%Y-%m-%d').date()
    report = report_service.get_year_report(user_id, year=report_date.year)
    return jsonify(report.as_dict()) if report else ('', 404)


@jwt_required()
def get_report_by_year(year):
    """Get a year report for the specified year"""
    user_id = get_jwt_identity()
    report = report_service.get_year_report(user_id, year=int(year))
    return jsonify(report.as_dict()) if report else ('', 404)


@jwt_required()
def list_reports():
    """List all year reports for user"""
    user_id = get_jwt_identity()
    reports = report_service.list_reports(YearReport, user_id=user_id)
    return jsonify([r.as_dict() for r in reports])


@jwt_required()
def create_report():
    """Create or update a year report"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Extract year from data
    if 'date' in data:
        report_date = datetime.strptime(data.pop('date'), '%Y-%m-%d').date()
        year = report_date.year
    else:
        year = data.pop('year')

    # Check if report exists for this year
    existing_report = report_service.get_year_report(user_id, year=year)

    if existing_report:
        report = report_service.update_report(existing_report, data)
        return jsonify(report.as_dict()), 200
    else:
        report = report_service.create_year_report(user_id, year, data)
        return jsonify(report.as_dict()), 201


@jwt_required()
def update_report(report_id):
    """Update a year report"""
    user_id = get_jwt_identity()
    report = report_service.get_year_report(user_id, id=report_id)
    if not report:
        return ('', 404)

    data = request.get_json()
    updated = report_service.update_report(report, data)
    return jsonify(updated.as_dict())


@jwt_required()
def delete_report(report_id):
    """Delete a year report"""
    user_id = get_jwt_identity()
    report = report_service.get_year_report(user_id, id=report_id)
    if not report:
        return ('', 404)

    report_service.delete_report(report)
    return ('', 204)