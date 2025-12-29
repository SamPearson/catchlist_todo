from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.calendars.service import CalendarService
from src.api.utils.caldav_client import CalDAVClient
from src.database.base.exceptions import ValidationError

@jwt_required()
def list_calendars():
    user_id = int(get_jwt_identity())
    service = CalendarService(db.session)
    items = service.list_calendars(user_id)
    return jsonify([c.as_dict() for c in items])

@jwt_required()
def create_calendar():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = CalendarService(db.session)
@jwt_required()
def discover_calendars():
    """POST /api/calendars/discover - List remote calendars"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    client = CalDAVClient(data.get('url'), data.get('username'), data.get('password'))
    service = CalendarService(db.session)
    try:
        remote_list = service.discover_remote_calendars(client)
        return jsonify(remote_list)
    except ValidationError as e:
        return jsonify({"error": e.message}), 400

@jwt_required()
def sync_calendar():
    """POST /api/calendars/sync - Sync a specific remote UID"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    remote_uid = data.get('remote_uid')
    
    if not remote_uid:
        return jsonify({"error": "remote_uid is required"}), 400

    client = CalDAVClient(data.get('url'), data.get('username'), data.get('password'))
    service = CalendarService(db.session)
    try:
        result = service.sync_calendar(user_id, remote_uid, client)
        return jsonify(result)
    except ValidationError as e:
        return jsonify({"error": e.message}), 400

@jwt_required()
def list_calendars():
    user_id = int(get_jwt_identity())
    service = CalendarService(db.session)
    items = service.list_calendars(user_id)
    return jsonify([c.as_dict() for c in items])

@jwt_required()
def create_calendar():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = CalendarService(db.session)
    cal = service.create_calendar(user_id, data)
    return jsonify(cal.as_dict()), 201