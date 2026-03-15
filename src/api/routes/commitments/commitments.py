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
from src.database.users.user import User
from src.utils.timezone import to_utc, validate_timezone


def _get_user_timezone(user_id: int) -> str | None:
    """Get user's timezone, or None if user not found or no timezone set."""
    user = User.query.get(user_id)
    if user and getattr(user, "timezone", None):
        return user.timezone
    return None


def _parse_datetime(value: str) -> datetime | None:
    """Parse ISO format datetime string. Returns None if invalid."""
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _serialize_commitment(commitment, user_tz: str) -> dict:
    """
    Convert a commitment to API-friendly dict with local times.

    Transforms:
    - start_at_utc -> start_at (converted to local time)
    - due_at_utc -> due_at (converted to local time)
    """
    from src.utils.timezone import from_utc

    data = commitment.as_dict()

    # Convert UTC timestamps to local time for API response
    if data.get("start_at_utc"):
        start_utc = datetime.fromisoformat(data["start_at_utc"])
        start_local = from_utc(start_utc, user_tz)
        data["start_at"] = start_local.isoformat()
    else:
        data["start_at"] = None

    if data.get("due_at_utc"):
        due_utc = datetime.fromisoformat(data["due_at_utc"])
        due_local = from_utc(due_utc, user_tz)
        data["due_at"] = due_local.isoformat()
    else:
        data["due_at"] = None

    # Remove internal UTC fields from API response
    data.pop("start_at_utc", None)
    data.pop("due_at_utc", None)

    return data


@jwt_required()
def list_commitments():
    user_id = int(get_jwt_identity())
    user_tz = _get_user_timezone(user_id)
    if not user_tz:
        user_tz = "UTC"  # Fallback to UTC if user has no timezone set
    
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

    return jsonify([_serialize_commitment(c, user_tz) for c in items])


@jwt_required()
def get_commitment(commitment_id: int):
    user_id = int(get_jwt_identity())
    user_tz = _get_user_timezone(user_id)
    if not user_tz:
        user_tz = "UTC"
    
    service = CommitmentService(session=db.session)
    c = service.get(user_id=user_id, commitment_id=commitment_id)
    
    if not c:
        return ("", 404)
    
    return jsonify(_serialize_commitment(c, user_tz))


@jwt_required()
def delete_commitment(commitment_id: int):
    user_id = int(get_jwt_identity())
    service = CommitmentService(session=db.session)
    ok = service.delete(user_id=user_id, commitment_id=commitment_id)
    return ("", 204) if ok else ("", 404)


@jwt_required()
def create_soft_commitment():
    user_id = int(get_jwt_identity())
    user_tz = _get_user_timezone(user_id)
    if not user_tz:
        user_tz = "UTC"
    
    data = request.get_json() or {}

    # Handle timeframe specification - either direct ID or kind + reference_date
    timeframe_id = None
    
    if "timeframe_id" in data and ("timeframe_kind" in data or "reference_date" in data):
        return jsonify({
            "error": "Provide either 'timeframe_id' OR ('timeframe_kind' and 'reference_date'), not both."
        }), 400
    
    if "timeframe_id" in data:
        # Direct timeframe ID provided
        timeframe_id = data["timeframe_id"]
    elif "timeframe_kind" in data and "reference_date" in data:
        # Derive timeframe from kind + date
        from src.database.timeframes.service import TimeframeService
        
        tz_error = validate_timezone(user_tz)
        if tz_error:
            return jsonify({"error": tz_error}), 400
        
        # Parse reference_date (expects local time)
        reference_date_local = _parse_datetime(data["reference_date"])
        if reference_date_local is None:
            return jsonify({"error": "Invalid reference_date format. Expected ISO datetime."}), 400

        
        # Get or create the appropriate timeframe
        timeframe_service = TimeframeService(session=db.session)
        try:
            timeframe = timeframe_service.get_or_create_for_date(
                user_id=user_id,
                kind=data["timeframe_kind"],
                local_date=reference_date_local,
                timezone=user_tz
            )
            timeframe_id = timeframe.id
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({
            "error": "Must provide either 'timeframe_id' OR both 'timeframe_kind' and 'reference_date'."
        }), 400

    # Validate other required fields
    required = {"target_type", "target_id"}
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Create the soft commitment with the derived or provided timeframe_id
    service = CommitmentService(session=db.session)
    try:
        c = service.create_soft(
            user_id=user_id,
            target_type=data["target_type"],
            target_id=int(data["target_id"]),
            timeframe_id=int(timeframe_id),
            status=data.get("status"),
            notes=data.get("notes"),
        )
        return jsonify(_serialize_commitment(c, user_tz)), 201
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
    """
    Create a hard commitment with a specific due time.
    
    Request body:
    {
        "target_type": "task|routine|session",  # project not allowed
        "target_id": integer,
        "due_at": "ISO datetime string",        # in user's local timezone
        "start_at": "ISO datetime string",      # optional, in user's local timezone
        "status": "planned|done|...",           # optional, defaults to planned
        "notes": "string"                       # optional
    }
    
    The day timeframe is automatically derived from due_at.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    # Validate required fields
    required = {"target_type", "target_id", "due_at"}
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Get and validate user timezone
    user_tz = _get_user_timezone(user_id)
    if not user_tz:
        return jsonify({"error": "User timezone not configured"}), 400
    
    tz_error = validate_timezone(user_tz)
    if tz_error:
        return jsonify({"error": tz_error}), 400

    # Parse due_at (required) - expects local time
    due_at_local = _parse_datetime(data["due_at"])
    if due_at_local is None:
        return jsonify({"error": "Invalid due_at format. Expected ISO datetime."}), 400

    # Parse start_at (optional) - expects local time
    start_at_utc = None
    if data.get("start_at"):
        start_at_local = _parse_datetime(data["start_at"])
        if start_at_local is None:
            return jsonify({"error": "Invalid start_at format. Expected ISO datetime."}), 400
        start_at_utc = to_utc(start_at_local, user_tz)

    # Convert due_at to UTC
    due_at_utc = to_utc(due_at_local, user_tz)

    # Create the hard commitment (service handles timeframe derivation)
    service = CommitmentService(session=db.session)
    try:
        c = service.create_hard(
            user_id=user_id,
            target_type=data["target_type"],
            target_id=int(data["target_id"]),
            due_at_utc=due_at_utc,
            timezone=user_tz,
            start_at_utc=start_at_utc,
            status=data.get("status"),
            notes=data.get("notes"),
        )
        return jsonify(_serialize_commitment(c, user_tz)), 201
    except CommitmentTargetNotFound as e:
        return jsonify({"error": e.message}), 404
    except CommitmentConflict as e:
        return jsonify({"error": e.message}), 409
    except CommitmentValidationError as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def update_commitment(commitment_id: int):
    """
    Update a commitment's editable fields.

    Request body (all fields optional):
    {
        "status": "planned|done|skipped|canceled|missed",
        "notes": "string",
        "due_at": "ISO datetime string",    # local time, hard commitments only
        "start_at": "ISO datetime string"   # local time, hard commitments only
    }

    Cannot change: target_type, target_id, timeframe_id
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    user_tz = _get_user_timezone(user_id)
    if not user_tz:
        return jsonify({"error": "User timezone not configured"}), 400

    tz_error = validate_timezone(user_tz)
    if tz_error:
        return jsonify({"error": tz_error}), 400

    # At least one field must be provided
    editable_fields = {"status", "notes", "due_at", "start_at"}
    provided_fields = set(data.keys()) & editable_fields
    if not provided_fields:
        return jsonify({
            "error": f"At least one editable field required: {', '.join(sorted(editable_fields))}"
        }), 400

    # Build update kwargs
    update_kwargs = {}

    # Handle status
    if "status" in data:
        update_kwargs["status"] = data["status"]

    # Handle notes
    if "notes" in data:
        update_kwargs["notes"] = data["notes"]

    service = CommitmentService(session=db.session)

    # Handle timestamp updates (due_at and start_at)
    # These require timezone conversion from local to UTC
    if "due_at" in data or "start_at" in data:

        if "due_at" in data:
            if data["due_at"] is None:
                # Clear due_at using dedicated method
                updated = service.clear_due_at(user_id=user_id, commitment_id=commitment_id)
                if not updated:
                    return ("", 404)
            else:
                # Apply changes to due datetime
                due_at_local = _parse_datetime(data["due_at"])
                if due_at_local is None:
                    return jsonify({"error": "Invalid due_at format. Expected ISO datetime."}), 400
                update_kwargs["due_at_utc"] = to_utc(due_at_local, user_tz)

        if "start_at" in data:
            if data["start_at"] is None:
                # Clear start_at using dedicated method
                updated = service.clear_start_at(user_id=user_id, commitment_id=commitment_id)
                if not updated:
                    return ("", 404)
            else:
                # Apply changes to start datetime
                start_at_local = _parse_datetime(data["start_at"])
                if start_at_local is None:
                    return jsonify({"error": "Invalid start_at format. Expected ISO datetime."}), 400
                update_kwargs["start_at_utc"] = to_utc(start_at_local, user_tz)

    try:
        updated = service.update(user_id=user_id, commitment_id=commitment_id, **update_kwargs)
        if not updated:
            return ("", 404)
        return jsonify(_serialize_commitment(updated, user_tz))
    except CommitmentValidationError as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400