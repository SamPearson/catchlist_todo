from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from src.database.db import db
from src.database.reports.report_service import ReportService, ReportValidationError


def get_report_service():
    return ReportService(db.session)


@jwt_required()
def get_report(report_id):
    """Get a specific report"""
    user_id = get_jwt_identity()
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    return jsonify(report.as_dict()) if report else ('', 404)


@jwt_required()
def list_reports():
    """List all reports for the current user"""
    user_id = get_jwt_identity()
    kind = request.args.get('kind')
    service = get_report_service()
    reports = service.list_reports(user_id, kind=kind)
    return jsonify([report.as_dict() for report in reports])


@jwt_required()
def create_report():
    """
    Create a new report for an existing timeframe.

    Body:
    - timeframe_id (required): ID of the timeframe
    - template_id (optional): Template to apply
    - plan, reason, pre_notes, post_notes (optional): Text fields
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'timeframe_id' not in data:
        return jsonify({'error': 'timeframe_id is required'}), 400

    service = get_report_service()
    try:
        template_id = data.pop('template_id', None)
        timeframe_id = data.pop('timeframe_id')
        report = service.create_report(
            user_id=user_id,
            timeframe_id=timeframe_id,
            data=data,
            template_id=template_id
        )
        return jsonify(report.as_dict()), 201
    except ReportValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def get_or_create_for_date():
    """
    Get or create a report for a specific date and timeframe kind.
    This is the primary workflow for accessing reports.

    Body:
    - kind (required): day, week, month, season, year
    - date (required): ISO date string (YYYY-MM-DD)
    - timezone (required): User's timezone (e.g., "America/Chicago")
    - template_id (optional): Specific template to use if creating
    - use_default_template (optional): Whether to use default template if creating (default true)
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    required_fields = ['kind', 'date', 'timezone']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    try:
        local_day = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    service = get_report_service()
    try:
        report, created = service.get_or_create_report(
            user_id=user_id,
            kind=data['kind'],
            local_day=local_day,
            user_tz=data['timezone'],
            template_id=data.get('template_id'),
            use_default_template=data.get('use_default_template', True)
        )
        status_code = 201 if created else 200
        return jsonify(report.as_dict()), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@jwt_required()
def update_report(report_id):
    """Update a report's text fields"""
    user_id = get_jwt_identity()
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    if not report:
        return ('', 404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    try:
        updated_report = service.update_report(report, data)
        return jsonify(updated_report.as_dict())
    except ReportValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def delete_report(report_id):
    """Delete a report"""
    user_id = get_jwt_identity()
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    if not report:
        return ('', 404)

    service.delete_report(report)
    return ('', 204)


@jwt_required()
def get_report_metrics(report_id):
    """Get all metric values for a report"""
    user_id = get_jwt_identity()
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    if not report:
        return ('', 404)

    metrics = service.get_metric_values(report_id, user_id)
    return jsonify([m.as_dict() for m in metrics])


@jwt_required()
def set_report_metrics(report_id):
    """
    Bulk set metric values on a report.

    Body: Object with metric_type_id keys and values
    Example: {"1": 8, "2": 7.5, "3": true}
    """
    user_id = get_jwt_identity()
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    if not report:
        return ('', 404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No metric data provided'}), 400

    try:
        # Convert string keys to int
        values = {int(k): v for k, v in data.items()}
        metrics = service.bulk_set_metric_values(report, values, user_id)
        return jsonify([m.as_dict() for m in metrics])
    except (ValueError, ReportValidationError) as e:
        return jsonify({'error': str(e)}), 400


@jwt_required()
def set_metric_value(report_id, metric_type_id):
    """
    Set a single metric value on a report.

    Body: {"value": <int|float|bool|null>}
    """
    user_id = get_jwt_identity()
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    if not report:
        return ('', 404)

    data = request.get_json()
    if data is None or 'value' not in data:
        return jsonify({'error': 'value field is required'}), 400

    try:
        metric = service.set_metric_value(report, metric_type_id, data['value'], user_id)
        return jsonify(metric.as_dict())
    except ReportValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def remove_metric_value(report_id, metric_type_id):
    """Remove a metric value from a report"""
    user_id = get_jwt_identity()
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    if not report:
        return ('', 404)

    service.remove_metric_value(report, metric_type_id, user_id)
    return ('', 204)