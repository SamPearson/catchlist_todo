from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.db import db
from src.database.commitments.service import (
    CommitmentService,
    CommitmentConflict,
    CommitmentValidationError,
    CommitmentTargetNotFound,
    CommitmentTimeframeNotFound,
)
from src.database.timeframes.service import TimeframeService
from src.utils.timezone import to_utc


@jwt_required()
def list_commitments():
    user_id = int(get_jwt_identity())
    timeframe_id = request.args.get("timeframe_id")
    service = CommitmentService(session=db.session)

    if timeframe_id is not None:
        try:
            timeframe_id = int(timeframe_id)
        except ValueError:
            return jsonify({"error": "timeframe_id must be an integer."}), 400
        items = service.list(user_id=user_id, timeframe_id=timeframe_id)
    else:
        items = service.list(user_id=user_id)

    return jsonify([c.as_dict() for c in items])


@jwt_required()
def get_commitment(commitment_id: int):
    user_id = int(get_jwt_identity())
    service = CommitmentService(session=db.session)
    c = service.get(user_id=user_id, commitment_id=commitment_id)
    return jsonify(c.as_dict()) if c else ("", 404)


@jwt_required()
def delete_commitment(commitment_id: int):
    user_id = int(get_jwt_identity())
    service = CommitmentService(session=db.session)
    ok = service.delete(user_id=user_id, commitment_id=commitment_id)
    return ("", 204) if ok else ("", 404)


@jwt_required()
def create_soft_commitment():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    required = {"target_type", "target_id", "timeframe_id"}
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    service = CommitmentService(session=db.session)
    try:
        c = service.create_soft(
            user_id=user_id,
            target_type=data["target_type"],
            target_id=int(data["target_id"]),
            timeframe_id=int(data["timeframe_id"]),
            status=data.get("status"),
            notes=data.get("notes"),
        )
        return jsonify(c.as_dict()), 201
    except CommitmentTargetNotFound as e:
        return jsonify({"error": e.message}), 404
    except CommitmentTimeframeNotFound as e:
        return jsonify({"error": e.message}), 404
    except CommitmentConflict as e:
        return jsonify({"error": e.message}), 409
    except CommitmentValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def create_hard_commitment():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    required = {"target_type", "target_id", "due_at"}
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Get user's timezone from database
    from src.database.users.user import User
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user_tz = user.timezone
    
    try:
        # Parse timestamps as if they're in the user's local timezone
        due_at_local = datetime.fromisoformat(data["due_at"])
        start_at_local = None
        if data.get("start_at_utc"):
            start_at_local = datetime.fromisoformat(data["start_at_utc"])
        
        # Convert to UTC
        due_at_utc = to_utc(due_at_local, user_tz)
        start_at_utc = to_utc(start_at_local, user_tz) if start_at_local else None
        
        # Get or create the DAY timeframe for this UTC timestamp
        timeframe_service = TimeframeService(session=db.session)
        day_tf = timeframe_service.get_or_create_for_utc(
            user_id=user_id,
            kind=TimeframeService.KIND_DAY,
            utc_dt=due_at_utc,
            user_tz=user_tz,
        )
        
        service = CommitmentService(session=db.session)
        c = service.create_hard(
            user_id=user_id,
            target_type=data["target_type"],
            target_id=int(data["target_id"]),
            timeframe_id=day_tf.id,
            due_at_utc=due_at_utc,
            start_at_utc=start_at_utc,
            status=data.get("status"),
            notes=data.get("notes"),
        )
        return jsonify(c.as_dict()), 201
    except CommitmentTargetNotFound as e:
        return jsonify({"error": e.message}), 404
    except CommitmentTimeframeNotFound as e:
        return jsonify({"error": e.message}), 404
    except CommitmentConflict as e:
        return jsonify({"error": e.message}), 409
    except CommitmentValidationError as e:
        return jsonify({"error": e.message}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid timestamp format: {str(e)}"}), 400


@jwt_required()
def update_commitment_status(commitment_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if "status" not in data:
        return jsonify({"error": "Missing required field: status"}), 400

    service = CommitmentService(session=db.session)
    try:
        updated = service.set_status(
            user_id=user_id,
            commitment_id=commitment_id,
            status=data["status"],
        )
        return jsonify(updated.as_dict()) if updated else ("", 404)
    except CommitmentValidationError as e:
        return jsonify({"error": e.message}), 400