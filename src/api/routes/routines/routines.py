from datetime import datetime

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.routines.service import RoutineService, RoutineValidationError
from src.config.caldav_client import CalDAVClient


@jwt_required()
def list_routines():
    user_id = int(get_jwt_identity())
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    service = RoutineService(db.session)
    items = service.list_routines(user_id, active_only=active_only)
    return jsonify([r.as_dict() for r in items])


@jwt_required()
def get_routine(routine_id: int):
    user_id = int(get_jwt_identity())
    service = RoutineService(db.session)
    routine = service.get_routine(routine_id, user_id)
    return jsonify(routine.as_dict()) if routine else ('', 404)


@jwt_required()
def create_routine():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = RoutineService(db.session)
    try:
        routine = service.create_routine(user_id, data)
        return jsonify(routine.as_dict()), 201
    except RoutineValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def update_routine(routine_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = RoutineService(db.session)
    try:
        updated = service.update_routine(routine_id, user_id, data)
        return jsonify(updated.as_dict()) if updated else ('', 404)
    except RoutineValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def delete_routine(routine_id: int):
    user_id = int(get_jwt_identity())
    service = RoutineService(db.session)
    return ('', 204) if service.delete_routine(routine_id, user_id) else ('', 404)


@jwt_required()
def import_routines():
    """Migrated CalDAV import logic using new Service/Repo pattern"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    url, username, password = data.get('url'), data.get('username'), data.get('password')
    if not all([url, username, password]):
        return jsonify({"error": "Missing CalDAV credentials"}), 400

    client = CalDAVClient(url, username, password)
    if not client.connect():
        return jsonify({"error": "Failed to connect to CalDAV server"}), 400

    calendars = client.get_calendars()
    if not calendars:
        return jsonify({"error": "No calendars found"}), 404

    # Use first calendar (matching legacy behavior)
    events = client.get_events(calendars[0].url)
    service = RoutineService(db.session)
    imported_count = 0

    for event in events:
        # Check if already exists via repo check in service
        existing = service.repo.find_by_external_uid(user_id, event.uid)
        if existing:
            continue

        service.create_routine(user_id, {
            "title": event.summary,
            "description": event.description,
            "rrule": event.rrule,
            "external_uid": event.uid,
            "external_source": 'caldav',
            "timezone": event.timezone
        })
        imported_count += 1

    return jsonify({"success": True, "imported_count": imported_count})


@jwt_required()
def expand_routine(routine_id: int):
    """POST /api/routines/<id>/expand?start=2025-01-01T00:00:00&end=2025-01-07T00:00:00"""
    user_id = int(get_jwt_identity())
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    if not start_str or not end_str:
        return jsonify({"error": "start and end ISO timestamps required"}), 400
        
    service = RoutineService(db.session)
    try:
        count = service.generate_sessions_from_rule(
            routine_id, 
            user_id, 
            datetime.fromisoformat(start_str), 
            datetime.fromisoformat(end_str)
        )
        return jsonify({"message": f"Successfully expanded routine into {count} sessions"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400