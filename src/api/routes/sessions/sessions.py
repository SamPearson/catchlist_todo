import logging
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.sessions.session_service import SessionService, SessionValidationError
from src.database.sessions.session_presenter import SessionPresenter
from src.database.base.exceptions import EntityNotFoundError
from src.utils.timezone import parse_dt, to_utc, from_utc, get_user_timezone


@jwt_required()
def list_sessions():
    user_id = int(get_jwt_identity())
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({"error": "start and end ISO dates required"}), 400

    # Extract optional filters from query params
    statuses = request.args.getlist('status')  # Repeated param: status=completed&status=skipped
    tag_names = request.args.getlist('tags')   # Repeated param: tags=fitness&tags=cardio
    principle_names = request.args.getlist('principles')  # Repeated param: principles=consistency&principles=growth
    routine_id_str = request.args.get('routine_id')

    # Validate routine_id if provided
    routine_id = None
    if routine_id_str:
        try:
            routine_id = int(routine_id_str)
        except ValueError:
            return jsonify({"error": "routine_id must be an integer"}), 400

    service = SessionService(db.session)
    try:
        # Get user timezone
        user_timezone = get_user_timezone(user_id)

        # Parse input times as user timezone
        start = parse_dt(start_str)
        end = parse_dt(end_str)

        # Get filtered sessions
        items = service.list_sessions_for_window_filtered(
            user_id=user_id,
            start=start,
            end=end,
            statuses=statuses if statuses else None,
            tag_names=tag_names if tag_names else None,
            principle_names=principle_names if principle_names else None,
            routine_id=routine_id
        )

        # Present sessions with times converted to user timezone
        session_dicts = SessionPresenter.present_list_for_user(items, user_timezone)

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
    try:
        session_obj = service.get_session(user_id, session_id)
    except EntityNotFoundError:
        return '', 404

    # Get user timezone and present session
    user_timezone = get_user_timezone(user_id)
    session_dict = SessionPresenter.present_for_user(session_obj, user_timezone)

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

        # Parse input times as user timezone (naive datetimes)
        if 'start_time' in data:
            data['start_time'] = parse_dt(data['start_time'])
        if 'end_time' in data:
            data['end_time'] = parse_dt(data['end_time'])

        session_obj = service.create_session(
            user_id,
            routine_id,
            data,
            inherit_tags=inherit_tags,
            inherit_principles=inherit_principles
        )

        # Present session with times converted to user timezone
        session_dict = SessionPresenter.present_for_user(session_obj, user_timezone)

        return jsonify(session_dict), 201
    except (SessionValidationError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def update_session(session_id: int):
    """PATCH /api/sessions/{id} - Update session properties (excludes status)"""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    service = SessionService(db.session)

    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    # Check for disallowed fields
    disallowed_fields = {'status', 'routine_id', 'user_id', 'id', 'created_at', 'updated_at', 'timezone'}
    if any(field in data for field in disallowed_fields):
        if 'status' in data:
            return jsonify({
                'error': 'Cannot update status via this endpoint. Use PATCH /api/sessions/{id}/status instead. '
                         'Cannot update read-only fields (id, user_id, routine_id, created_at, updated_at, timezone).'
            }), 400
        else:
            return jsonify({
                'error': 'Cannot update read-only fields (id, user_id, routine_id, created_at, updated_at, timezone).'
            }), 400

    try:
        user_timezone = get_user_timezone(user_id)

        # Parse input times as user timezone (naive datetimes)
        if 'start_time' in data:
            data['start_time'] = parse_dt(data['start_time'])
        if 'end_time' in data:
            data['end_time'] = parse_dt(data['end_time'])

        updated = service.update_session(user_id, session_id, data)

        # Present session with times converted to user timezone
        session_dict = SessionPresenter.present_for_user(updated, user_timezone)

        return jsonify(session_dict)
    except EntityNotFoundError:
        return '', 404
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
        session_obj = service.set_session_status(user_id, session_id, status)

        # Get user timezone and present session
        user_timezone = get_user_timezone(user_id)
        session_dict = SessionPresenter.present_for_user(session_obj, user_timezone)

        return jsonify(session_dict)
    except EntityNotFoundError:
        return '', 404
    except SessionValidationError as e:
        return jsonify({'error': str(e)}), 400


@jwt_required()
def delete_session(session_id: int):
    user_id = int(get_jwt_identity())
    service = SessionService(db.session)
    try:
        service.delete_session(user_id, session_id)
        return '', 204
    except EntityNotFoundError:
        return '', 404