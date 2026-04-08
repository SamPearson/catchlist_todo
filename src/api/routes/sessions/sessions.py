import logging
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.sessions.service import SessionService, SessionValidationError
from src.utils.timezone import parse_dt, to_utc, from_utc
from src.database.users.models import User


def get_user_timezone(user_id):
    """Get the user's timezone or return UTC as default"""
    user = User.query.get(user_id)
    return user.timezone if user and hasattr(user, 'timezone') and user.timezone else "UTC"


@jwt_required()
def list_sessions():
    user_id = int(get_jwt_identity())
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({"error": "start and end ISO dates required"}), 400

    service = SessionService(db.session)
    try:
        # Get user timezone and convert input dates to UTC
        user_timezone = get_user_timezone(user_id)
        start = to_utc(parse_dt(start_str, user_timezone), user_timezone)
        end = to_utc(parse_dt(end_str, user_timezone), user_timezone)

        # Get sessions (stored in UTC)
        items = service.list_sessions_for_window(user_id, start, end)

        # Convert sessions to dicts and convert times to user timezone
        session_dicts = []
        for session in items:
            session_dict = session.as_dict()
            session_dict['start_time'] = from_utc(parse_dt(session_dict['start_time']), user_timezone).isoformat()
            session_dict['end_time'] = from_utc(parse_dt(session_dict['end_time']), user_timezone).isoformat()
            session_dicts.append(session_dict)

        return jsonify(session_dicts)
    except ValueError as e:
        return jsonify({"error": "Invalid date format"}), 400
    except Exception as e:
        logging.error(f"Unexpected error in list_sessions: {str(e)}")
        return jsonify({"error": str(e)}), 500


@jwt_required()
def get_session(session_id: int):
    user_id = int(get_jwt_identity())
    service = SessionService(db.session)
    session_obj = service.get_session(session_id, user_id)
    
    if not session_obj:
        return '', 404

    # Convert UTC times to user timezone
    user_timezone = get_user_timezone(user_id)
    session_dict = session_obj.as_dict()
    session_dict['start_time'] = from_utc(parse_dt(session_dict['start_time']), user_timezone).isoformat()
    session_dict['end_time'] = from_utc(parse_dt(session_dict['end_time']), user_timezone).isoformat()

    return jsonify(session_dict)


@jwt_required()
def create_session(routine_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = SessionService(db.session)
    try:
        user_timezone = get_user_timezone(user_id)

        # Parse the inheritance query parameters (default: both true)
        inherit_tags = request.args.get('inherit_tags', 'true').lower() == 'true'
        inherit_principles = request.args.get('inherit_principles', 'true').lower() == 'true'

        # Convert input times from user timezone to UTC
        if 'start_time' in data:
            data['start_time'] = to_utc(parse_dt(data['start_time'], user_timezone), user_timezone)
        if 'end_time' in data:
            data['end_time'] = to_utc(parse_dt(data['end_time'], user_timezone), user_timezone)

        session_obj = service.create_session(
            user_id,
            routine_id,
            data,
            inherit_tags=inherit_tags,
            inherit_principles=inherit_principles
        )

        # Convert response times back to user timezone
        session_dict = session_obj.as_dict()
        session_dict['start_time'] = from_utc(parse_dt(session_dict['start_time']), user_timezone).isoformat()
        session_dict['end_time'] = from_utc(parse_dt(session_dict['end_time']), user_timezone).isoformat()

        return jsonify(session_dict), 201
    except (SessionValidationError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def update_session(session_id: int):
    """PATCH /api/sessions/{id} - Update session properties (excludes status)"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = SessionService(db.session)

    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    # Check for disallowed fields
    disallowed_fields = {'status', 'routine_id', 'user_id', 'id', 'created_at', 'updated_at'}
    if any(field in data for field in disallowed_fields):
        if 'status' in data:
            return jsonify({
                'error': 'Cannot update status via this endpoint. Use PATCH /api/sessions/{id}/status instead. '
                         'Cannot update read-only fields (id, user_id, routine_id, created_at, updated_at).'
            }), 400
        else:
            return jsonify({
                'error': 'Cannot update read-only fields (id, user_id, routine_id, created_at, updated_at).'
            })

    try:
        user_timezone = get_user_timezone(user_id)

        # Convert input times from user timezone to UTC
        if 'start_time' in data:
            data['start_time'] = to_utc(parse_dt(data['start_time'], user_timezone), user_timezone)
        if 'end_time' in data:
            data['end_time'] = to_utc(parse_dt(data['end_time'], user_timezone), user_timezone)

        updated = service.update_session(session_id, user_id, data)

        if not updated:
            return '', 404

        # Convert response times back to user timezone
        session_dict = updated.as_dict()
        session_dict['start_time'] = from_utc(parse_dt(session_dict['start_time']), user_timezone).isoformat()
        session_dict['end_time'] = from_utc(parse_dt(session_dict['end_time']), user_timezone).isoformat()

        return jsonify(session_dict)
    except (SessionValidationError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def set_session_status(session_id: int):
    """PATCH /api/sessions/{id}/status - Set session status to one of: scheduled, completed, skipped, cancelled"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = SessionService(db.session)

    if 'status' not in data:
        return jsonify({'error': 'status field is required'}), 400

    status = data['status']

    try:
        session_obj = service.set_session_status(session_id, user_id, status)

        if not session_obj:
            return '', 404

        # Convert UTC times to user timezone
        user_timezone = get_user_timezone(user_id)
        session_dict = session_obj.as_dict()
        session_dict['start_time'] = from_utc(parse_dt(session_dict['start_time']), user_timezone).isoformat()
        session_dict['end_time'] = from_utc(parse_dt(session_dict['end_time']), user_timezone).isoformat()

        return jsonify(session_dict)
    except SessionValidationError as e:
        return jsonify({'error': str(e)}), 400


@jwt_required()
def delete_session(session_id: int):
    user_id = int(get_jwt_identity())
    service = SessionService(db.session)
    return ('', 204) if service.delete_session(session_id, user_id) else ('', 404)



