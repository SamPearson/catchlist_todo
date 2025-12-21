from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.sessions.service import SessionService, SessionValidationError
from datetime import datetime


@jwt_required()
def list_sessions():
    user_id = int(get_jwt_identity())
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({"error": "start and end ISO dates required"}), 400

    service = SessionService(db.session)
    try:
        start = datetime.fromisoformat(start_str)
        end = datetime.fromisoformat(end_str)
        items = service.list_sessions_for_window(user_id, start, end)
        return jsonify([s.as_dict() for s in items])
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400


@jwt_required()
def get_session(session_id: int):
    user_id = int(get_jwt_identity())
    service = SessionService(db.session)
    session_obj = service.get_session(session_id, user_id)
    return jsonify(session_obj.as_dict()) if session_obj else ('', 404)


@jwt_required()
def create_session(routine_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = SessionService(db.session)
    try:
        # Convert strings to objects for service
        if 'start_time' in data: data['start_time'] = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data: data['end_time'] = datetime.fromisoformat(data['end_time'])

        session_obj = service.create_session(user_id, routine_id, data)
        return jsonify(session_obj.as_dict()), 201
    except (SessionValidationError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def update_session(session_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = SessionService(db.session)
    try:
        if 'start_time' in data: data['start_time'] = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data: data['end_time'] = datetime.fromisoformat(data['end_time'])

        updated = service.update_session(session_id, user_id, data)
        return jsonify(updated.as_dict()) if updated else ('', 404)
    except (SessionValidationError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def delete_session(session_id: int):
    user_id = int(get_jwt_identity())
    service = SessionService(db.session)
    return ('', 204) if service.delete_session(session_id, user_id) else ('', 404)