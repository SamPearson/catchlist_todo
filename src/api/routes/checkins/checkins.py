from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.db import db
from src.database.checkins.service import CheckinService, CheckinTargetNotFound, CheckinValidationError


@jwt_required()
def create_checkin():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    required = {"target_type", "target_id", "note"}
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    service = CheckinService(session=db.session)
    try:
        checkin = service.create(
            user_id=user_id,
            target_type=data["target_type"],
            target_id=int(data["target_id"]),
            note=data["note"],
            occurred_at=data.get("occurred_at"),
        )
        return jsonify(checkin.as_dict()), 201
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

    service = CheckinService(session=db.session)
    try:
        items = service.list_for_target(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            limit=limit,
            offset=offset,
        )
        return jsonify([c.as_dict() for c in items])
    except CheckinTargetNotFound as e:
        return jsonify({"error": e.message}), 404
    except CheckinValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def get_checkin(checkin_id: int):
    user_id = int(get_jwt_identity())
    service = CheckinService(session=db.session)
    c = service.get(user_id=user_id, checkin_id=checkin_id)
    return jsonify(c.as_dict()) if c else ("", 404)


@jwt_required()
def delete_checkin(checkin_id: int):
    user_id = int(get_jwt_identity())
    service = CheckinService(session=db.session)
    ok = service.delete(user_id=user_id, checkin_id=checkin_id)
    return ("", 204) if ok else ("", 404)