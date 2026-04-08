from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.calendars.service import CalendarService
from src.api.utils.caldav_client import CalDAVClient, CalDAVConnectionError
from src.database.base.exceptions import ValidationError
import re

@jwt_required()
def list_calendars():
    user_id = int(get_jwt_identity())
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    service = CalendarService(db.session)
    items = service.list_calendars(user_id, include_inactive=include_inactive)
    return jsonify([c.as_dict() for c in items])


@jwt_required()
def discover_calendars():
    """POST /api/calendars/discover - List remote calendars"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    # Validate required fields
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')
    
    if not url:
        return jsonify({"error": "url is required"}), 400
    
    if not username:
        return jsonify({"error": "username is required"}), 400
    
    if not password:
        return jsonify({"error": "password is required"}), 400

    client = CalDAVClient(url, username, password)
    service = CalendarService(db.session)
    try:
        remote_list = service.discover_remote_calendars(client)
        return jsonify(remote_list)
    except CalDAVConnectionError as e:
        return jsonify({"error": str(e)}), 401
    except ValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def sync_calendar():
    """POST /api/calendars/sync - Sync a specific remote UID"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    # Validate required fields
    remote_uid = data.get('remote_uid')
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')

    if not remote_uid:
        return jsonify({"error": "remote_uid is required"}), 400
    
    if not url:
        return jsonify({"error": "url is required"}), 400
    
    if not username:
        return jsonify({"error": "username is required"}), 400
    
    if not password:
        return jsonify({"error": "password is required"}), 400

    client = CalDAVClient(url, username, password)
    service = CalendarService(db.session)
    try:
        result = service.sync_calendar(user_id, remote_uid, client)
        return jsonify(result)
    except CalDAVConnectionError as e:
        return jsonify({"error": str(e)}), 401
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def get_calendar(calendar_id):
    """GET /api/calendars/<calendar_id> - Get a specific calendar"""
    user_id = int(get_jwt_identity())
    service = CalendarService(db.session)

    calendar = service.get_calendar(calendar_id, user_id)
    if not calendar:
        return jsonify({"error": "Calendar not found"}), 404

    return jsonify(calendar.as_dict())


@jwt_required()
def create_calendar():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate request body exists
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    # Validate name field
    if 'name' not in data:
        return jsonify({"error": "Calendar name is required"}), 400
    
    name = data.get('name', '').strip()
    
    # Validate name is not empty or whitespace-only
    if not name:
        return jsonify({"error": "Calendar name cannot be empty"}), 400
    
    # Validate name length
    if len(name) > 200:
        return jsonify({"error": "Calendar name cannot exceed 200 characters"}), 400
    
    # Validate color format if provided
    if 'color' in data:
        color = data.get('color', '')
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return jsonify({"error": "Color must be in hex format (#RRGGBB)"}), 400
    
    service = CalendarService(db.session)
    try:
        cal = service.create_calendar(user_id, data)
        return jsonify(cal.as_dict()), 201
    except ValidationError as e:
        return jsonify({"error": e.message}), 400



@jwt_required()
def update_calendar(calendar_id):
    """PUT /api/calendars/<calendar_id> - Update a calendar"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate request body exists
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    # Don't allow updating the 'active' field via update endpoint
    if 'active' in data:
        return jsonify({"error": "Use /activate or /deactivate endpoints to change calendar status"}), 400
    
    # Validate name if provided
    if 'name' in data:
        name = data.get('name', '').strip()
        
        # Validate name is not empty or whitespace-only
        if not name:
            return jsonify({"error": "Calendar name cannot be empty"}), 400
        
        # Validate name length
        if len(name) > 200:
            return jsonify({"error": "Calendar name cannot exceed 200 characters"}), 400
    
    # Validate color format if provided
    if 'color' in data:
        color = data.get('color', '')
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return jsonify({"error": "Color must be in hex format (#RRGGBB)"}), 400
    
    service = CalendarService(db.session)

    try:
        calendar = service.update_calendar(user_id, calendar_id, data)
        if not calendar:
            return jsonify({"error": "Calendar not found"}), 404
        return jsonify(calendar.as_dict())
    except ValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def activate_calendar(calendar_id):
    """PUT /api/calendars/<calendar_id>/activate - Activate a calendar"""
    user_id = int(get_jwt_identity())
    
    # Parse cascade parameter (default: true)
    cascade = request.args.get('cascade', 'true').lower() == 'true'

    service = CalendarService(db.session)
    
    try:
        calendar = service.activate_calendar(user_id, calendar_id, cascade=cascade)
        if not calendar:
            return jsonify({"error": "Calendar not found"}), 404
        return jsonify(calendar.as_dict())
    except ValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def deactivate_calendar(calendar_id):
    """PUT /api/calendars/<calendar_id>/deactivate - Deactivate a calendar"""
    user_id = int(get_jwt_identity())
    
    # Parse cascade parameter (default: true)
    cascade = request.args.get('cascade', 'true').lower() == 'true'

    service = CalendarService(db.session)
    
    try:
        calendar = service.deactivate_calendar(user_id, calendar_id, cascade=cascade)
        if not calendar:
            return jsonify({"error": "Calendar not found"}), 404
        return jsonify(calendar.as_dict())
    except ValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def delete_calendar(calendar_id):
    """DELETE /api/calendars/<calendar_id> - Delete a calendar"""
    user_id = int(get_jwt_identity())
    service = CalendarService(db.session)

    if not service.delete_calendar(user_id, calendar_id):
        return jsonify({"error": "Calendar not found"}), 404

    return jsonify({"message": "Calendar deleted successfully"}), 204