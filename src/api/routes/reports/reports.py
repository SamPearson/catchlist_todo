from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from src.database.db import db
from src.database.reports.service import ReportService, ReportValidationError
from src.database.timeframes.service import TimeframeService
from src.database.users.user import User
from src.utils.timezone import compute_timeframe_bounds


def get_report_service():
    return ReportService(db.session)


def get_timeframe_service():
    return TimeframeService(db.session)


def get_user_timezone(user_id):
    """Get the user's timezone or return UTC as default"""
    user = User.query.get(user_id)
    return user.timezone if user and hasattr(user, 'timezone') and user.timezone else "UTC"


@jwt_required()
def get_report(report_id):
    """
    Get a specific report by ID
    
    Query params:
    - full (optional): If true, returns full representation with metadata (default: false)
    - commitment_scope (optional): How to include commitments:
        - 'window': All commitments in timeframe boundaries (default)
        - 'direct': Only commitments to this exact timeframe
        - 'none': Don't include commitments or stats
    """
    user_id = int(get_jwt_identity())
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    
    if not report:
        return ('', 404)
    
    # Parse query params
    full = request.args.get('full', 'false').lower() == 'true'
    commitment_scope = request.args.get('commitment_scope', 'window')
    
    # Validate commitment_scope
    if commitment_scope not in ('window', 'direct', 'none'):
        return jsonify({'error': "commitment_scope must be 'window', 'direct', or 'none'"}), 400
    
    return jsonify(service.build_report_dict(
        report,
        full=full,
        commitment_scope=commitment_scope,
    ))


@jwt_required()
def list_reports():
    """
    List reports for the current user.
    
    Query params:
    - timeframe_ids: Comma-separated list of timeframe IDs to filter by
    - full (optional): If true, returns full representation with metadata (default: false)
    - commitment_scope (optional): How to include commitments:
        - 'window': All commitments in timeframe boundaries (default)
        - 'direct': Only commitments to this exact timeframe
        - 'none': Don't include commitments or stats (recommended for list views)
    """
    user_id = int(get_jwt_identity())
    service = get_report_service()
    
    # Optional filtering by timeframe IDs
    timeframe_ids_param = request.args.get('timeframe_ids')
    if timeframe_ids_param:
        try:
            timeframe_ids = [int(id.strip()) for id in timeframe_ids_param.split(',')]
            reports = service.repo.list_by_timeframes(user_id=user_id, timeframe_ids=timeframe_ids)
        except ValueError:
            return jsonify({'error': 'Invalid timeframe_ids format'}), 400
    else:
        reports = service.repo.list_for_user(user_id)
    
    # Parse query params
    full = request.args.get('full', 'false').lower() == 'true'
    commitment_scope = request.args.get('commitment_scope', 'none')  # Default to 'none' for list views
    
    # Validate commitment_scope
    if commitment_scope not in ('window', 'direct', 'none'):
        return jsonify({'error': "commitment_scope must be 'window', 'direct', or 'none'"}), 400
    
    return jsonify([
        service.build_report_dict(
            report,
            full=full,
            commitment_scope=commitment_scope,
        )
        for report in reports
    ])


@jwt_required()
def get_or_create_for_date(kind, date):
    """
    Get or create a report for a specific date and timeframe kind.
    
    URL params:
    - kind: day, week, month, season, year
    - date: ISO date string (YYYY-MM-DD)
    
    Query params:
    - timezone (optional): User's timezone (e.g., "America/Chicago"). Defaults to user's stored timezone.
    - full (optional): If true, returns full representation with metadata (default: false)
    - commitment_scope (optional): How to include commitments:
        - 'window': All commitments in timeframe boundaries (default)
        - 'direct': Only commitments to this exact timeframe
        - 'none': Don't include commitments or stats
    
    Examples:
    - GET /api/reports/day/2026-01-17
    - GET /api/reports/day/2026-01-17?timezone=America/Chicago
    - GET /api/reports/week/2026-01-17
    - GET /api/reports/month/2026-01-17?commitment_scope=direct
    - GET /api/reports/season/2026-03-15?commitment_scope=none
    """
    user_id = int(get_jwt_identity())
    
    # Get timezone from query params or use user's default
    timezone = request.args.get('timezone')
    if not timezone:
        timezone = get_user_timezone(user_id)
    
    # Parse date
    try:
        local_day = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate kind
    valid_kinds = ['day', 'week', 'month', 'season', 'year']
    if kind not in valid_kinds:
        return jsonify({'error': f'Invalid kind. Must be one of: {", ".join(valid_kinds)}'}), 400
    
    # Compute timeframe bounds
    try:
        start_utc, end_utc, label = compute_timeframe_bounds(
            kind=kind,
            local_day=local_day,
            user_tz=timezone
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    # Get or create timeframe
    timeframe_service = get_timeframe_service()
    timeframe = timeframe_service.get_or_create_for_bounds(
        user_id=user_id,
        kind=kind,
        start_utc=start_utc,
        end_utc=end_utc,
        label=label,
    )
    
    # Get or create report
    report_service = get_report_service()
    
    try:
        report = report_service.get_or_create_for_timeframe(
            user_id=user_id,
            timeframe_id=timeframe.id,
        )
        
        # Parse query params
        full = request.args.get('full', 'false').lower() == 'true'
        commitment_scope = request.args.get('commitment_scope', 'window')
        
        # Validate commitment_scope
        if commitment_scope not in ('window', 'direct', 'none'):
            return jsonify({'error': "commitment_scope must be 'window', 'direct', or 'none'"}), 400
        
        return jsonify(report_service.build_report_dict(
            report,
            full=full,
            commitment_scope=commitment_scope,
        ))
    except ReportValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def update_report(report_id):
    """
    Update a report's text fields.
    
    Body:
    - plan (optional): Planning text
    - reason (optional): Reason/motivation text
    - pre_notes (optional): Notes before the timeframe
    - post_notes (optional): Notes after the timeframe
    
    Query params:
    - full (optional): If true, returns full representation with metadata (default: false)
    - commitment_scope (optional): How to include commitments:
        - 'window': All commitments in timeframe boundaries (default)
        - 'direct': Only commitments to this exact timeframe
        - 'none': Don't include commitments or stats
    """
    user_id = int(get_jwt_identity())
    service = get_report_service()
    report = service.get_report(report_id, user_id)
    if not report:
        return ('', 404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    try:
        updated_report = service.update_report(
            report_id=report_id,
            user_id=user_id,
            plan=data.get('plan'),
            reason=data.get('reason'),
            pre_notes=data.get('pre_notes'),
            post_notes=data.get('post_notes'),
        )
        
        # Parse query params
        full = request.args.get('full', 'false').lower() == 'true'
        commitment_scope = request.args.get('commitment_scope', 'window')
        
        # Validate commitment_scope
        if commitment_scope not in ('window', 'direct', 'none'):
            return jsonify({'error': "commitment_scope must be 'window', 'direct', or 'none'"}), 400
        
        return jsonify(service.build_report_dict(
            updated_report,
            full=full,
            commitment_scope=commitment_scope,
        ))
    except ReportValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def delete_report(report_id):
    """Delete a report"""
    user_id = int(get_jwt_identity())
    service = get_report_service()
    
    deleted = service.delete_report(report_id, user_id)
    return ('', 204) if deleted else ('', 404)

