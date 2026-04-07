from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.db import db
from src.database.checkins.service import CheckinService, CheckinTargetNotFound, CheckinValidationError
from src.database.users.models import User
from src.utils.timezone import parse_dt, to_utc, from_utc


def get_user_timezone(user_id):
    """Get the user's timezone or return UTC as default"""
    user = User.query.get(user_id)
    return user.timezone if user and hasattr(user, 'timezone') and user.timezone else "UTC"


def _localize_checkin(checkin_dict: dict, user_timezone: str) -> dict:
    """Convert UTC timestamps in checkin dict to user timezone"""
    if checkin_dict.get('occurred_at_utc'):
        checkin_dict['occurred_at'] = from_utc(
            parse_dt(checkin_dict['occurred_at_utc']), 
            user_timezone
        ).isoformat()
    # Remove the UTC field from response, return localized version
    checkin_dict.pop('occurred_at_utc', None)
    return checkin_dict


@jwt_required()
def create_checkin():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    required = {"target_type", "target_id", "note"}
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    user_timezone = get_user_timezone(user_id)

    # Convert occurred_at from user timezone to UTC if provided
    occurred_at_utc = None
    if data.get("occurred_at"):
        try:
            occurred_at_utc = to_utc(parse_dt(data["occurred_at"], user_timezone), user_timezone)
        except ValueError:
            return jsonify({"error": "Invalid occurred_at format. Expected ISO 8601 datetime."}), 400

    service = CheckinService(session=db.session)
    try:
        checkin = service.create(
            user_id=user_id,
            target_type=data["target_type"],
            target_id=int(data["target_id"]),
            note=data["note"],
            occurred_at_utc=occurred_at_utc,
        )
        return jsonify(_localize_checkin(checkin.as_dict(), user_timezone)), 201
    except CheckinTargetNotFound as e:
        return jsonify({"error": e.message}), 404
    except CheckinValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def list_checkins():
    user_id = int(get_jwt_identity())

    target_type = request.args.get("target_type")
    target_id = request.args.get("target_id")

    if not target_type or not target_id:
        return jsonify({"error": "target_type and target_id are required query params."}), 400

    try:
        target_id = int(target_id)
    except ValueError:
        return jsonify({"error": "target_id must be an integer."}), 400

    limit = request.args.get("limit", "50")
    offset = request.args.get("offset", "0")
    try:
        limit = int(limit)
        offset = int(offset)
    except ValueError:
        return jsonify({"error": "limit and offset must be integers."}), 400

    user_timezone = get_user_timezone(user_id)
    
    # Parse optional date range parameters
    start_date = None
    end_date = None
    
    if request.args.get("start_date"):
        try:
            start_date = to_utc(parse_dt(request.args.get("start_date"), user_timezone), user_timezone)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Expected ISO 8601 datetime."}), 400
    
    if request.args.get("end_date"):
        try:
            end_date = to_utc(parse_dt(request.args.get("end_date"), user_timezone), user_timezone)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Expected ISO 8601 datetime."}), 400

    service = CheckinService(session=db.session)
    try:
        items = service.list_for_target(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )
        return jsonify([_localize_checkin(c.as_dict(), user_timezone) for c in items])
    except CheckinTargetNotFound as e:
        return jsonify({"error": e.message}), 404
    except CheckinValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def list_all_checkins():
    """
    List all checkins for the authenticated user, optionally filtered by date range.
    
    Query params:
    - limit: max records to return (default 50)
    - offset: records to skip (default 0)
    - start_date: filter checkins on or after this date (ISO 8601)
    - end_date: filter checkins on or before this date (ISO 8601)
    """
    user_id = int(get_jwt_identity())

    limit = request.args.get("limit", "50")
    offset = request.args.get("offset", "0")
    try:
        limit = int(limit)
        offset = int(offset)
    except ValueError:
        return jsonify({"error": "limit and offset must be integers."}), 400

    user_timezone = get_user_timezone(user_id)
    
    # Parse optional date range parameters
    start_date = None
    end_date = None
    
    if request.args.get("start_date"):
        try:
            start_date = to_utc(parse_dt(request.args.get("start_date"), user_timezone), user_timezone)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Expected ISO 8601 datetime."}), 400
    
    if request.args.get("end_date"):
        try:
            end_date = to_utc(parse_dt(request.args.get("end_date"), user_timezone), user_timezone)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Expected ISO 8601 datetime."}), 400

    service = CheckinService(session=db.session)
    items = service.list_for_user(
        user_id=user_id,
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
    )
    return jsonify([_localize_checkin(c.as_dict(), user_timezone) for c in items])


@jwt_required()
def get_checkin(checkin_id: int):
    user_id = int(get_jwt_identity())
    service = CheckinService(session=db.session)
    checkin = service.get(user_id=user_id, checkin_id=checkin_id)
    
    if not checkin:
        return "", 404
    
    user_timezone = get_user_timezone(user_id)
    return jsonify(_localize_checkin(checkin.as_dict(), user_timezone))


@jwt_required()
def update_checkin(checkin_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    user_timezone = get_user_timezone(user_id)

    # Build update kwargs for service
    update_kwargs = {}
    
    if "note" in data:
        note = (data["note"] or "").strip()
        if not note:
            return jsonify({"error": "Note cannot be empty"}), 400
        update_kwargs["note"] = note

    if "occurred_at" in data:
        try:
            update_kwargs["occurred_at_utc"] = to_utc(
                parse_dt(data["occurred_at"], user_timezone), 
                user_timezone
            )
        except ValueError:
            return jsonify({"error": "Invalid occurred_at format. Expected ISO 8601 datetime."}), 400

    if not update_kwargs:
        return jsonify({"error": "No valid fields to update"}), 400

    service = CheckinService(session=db.session)
    try:
        updated = service.update(
            user_id=user_id,
            checkin_id=checkin_id,
            **update_kwargs
        )
        if not updated:
            return "", 404
        return jsonify(_localize_checkin(updated.as_dict(), user_timezone))
    except CheckinValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def delete_checkin(checkin_id: int):
    user_id = int(get_jwt_identity())
    service = CheckinService(session=db.session)
    ok = service.delete(user_id=user_id, checkin_id=checkin_id)
    return ("", 204) if ok else ("", 404)