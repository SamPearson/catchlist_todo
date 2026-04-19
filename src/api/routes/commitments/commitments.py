from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.timeframes.timeframe_service import TimeframeValidationError, UnsupportedTimeframeKind
from src.database.db import db
from src.database.commitments.commitment_service import (
    CommitmentService,
    CommitmentConflict,
    CommitmentValidationError,
    CommitmentTargetNotFound,
    CommitmentTimeframeNotFound,
)
from src.database.users.user_models import User
from src.utils.timezone import validate_timezone


def _get_user_timezone(user_id: int) -> str:
    """Get user's timezone, defaulting to UTC if not set."""
    user = User.query.get(user_id)
    if user and getattr(user, "timezone", None):
        return user.timezone
    return "UTC"


def _parse_datetime(value: str) -> datetime | None:
    """Parse ISO format datetime string. Returns None if invalid."""
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError, AttributeError):
        return None


@jwt_required()
def list_commitments():
    user_id = int(get_jwt_identity())
    user_tz = _get_user_timezone(user_id)

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

    return jsonify([c.as_dict(user_timezone=user_tz) for c in items])


@jwt_required()
def get_commitment(commitment_id: int):
    user_id = int(get_jwt_identity())
    user_tz = _get_user_timezone(user_id)

    service = CommitmentService(session=db.session)
    c = service.get(user_id=user_id, commitment_id=commitment_id)

    if not c:
        return ("", 404)

    return jsonify(c.as_dict(user_timezone=user_tz))


@jwt_required()
def delete_commitment(commitment_id: int):
    user_id = int(get_jwt_identity())
    service = CommitmentService(session=db.session)
    ok = service.delete(user_id=user_id, commitment_id=commitment_id)
    return ("", 204) if ok \
        else ({'error': f"Couldn't find commitment with ID {commitment_id}"}, 404)


@jwt_required()
def create_soft_commitment():
    user_id = int(get_jwt_identity())
    user_tz = _get_user_timezone(user_id)

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
        from src.database.timeframes.timeframe_service import TimeframeService

        tz_error = validate_timezone(user_tz)
        if tz_error:
            return jsonify({"error": tz_error}), 400

        # Parse reference_date (expects local date string YYYY-MM-DD)
        from datetime import datetime
        try:
            reference_date_local = datetime.strptime(data["reference_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid reference_date format. Expected YYYY-MM-DD."}), 400

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
        except UnsupportedTimeframeKind as e:
            return jsonify({"error": e.message}), 400
        except TimeframeValidationError as e:
            return jsonify({"error": e.message}), 400
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
        return jsonify(c.as_dict(user_timezone=user_tz)), 201
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
        "timezone": "America/Chicago",          # optional, defaults to user's timezone
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

    # Get timezone (from request or user default)
    user_tz = _get_user_timezone(user_id)
    timezone = data.get("timezone", user_tz)

    tz_error = validate_timezone(timezone)
    if tz_error:
        return jsonify({"error": tz_error}), 400

    # Parse due_at (required) - expects local time
    due_at_local = _parse_datetime(data["due_at"])
    if due_at_local is None:
        return jsonify({"error": "Invalid due_at format. Expected ISO datetime."}), 400

    # Parse start_at (optional) - expects local time
    start_at_local = None
    if data.get("start_at"):
        start_at_local = _parse_datetime(data["start_at"])
        if start_at_local is None:
            return jsonify({"error": "Invalid start_at format. Expected ISO datetime."}), 400

    # Create the hard commitment (service handles timezone conversion)
    service = CommitmentService(session=db.session)
    try:
        c = service.create_hard(
            user_id=user_id,
            target_type=data["target_type"],
            target_id=int(data["target_id"]),
            due_at=due_at_local,
            timezone=timezone,
            start_at=start_at_local,
            status=data.get("status"),
            notes=data.get("notes"),
        )
        return jsonify(c.as_dict(user_timezone=user_tz)), 201
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
        "start_at": "ISO datetime string",  # local time, hard commitments only
        "timezone": "America/Chicago"       # optional, defaults to user's timezone
    }

    Cannot change: target_type, target_id, timeframe_id
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    user_tz = _get_user_timezone(user_id)
    timezone = data.get("timezone", user_tz)

    tz_error = validate_timezone(timezone)
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
    update_kwargs = {"timezone": timezone}

    # Handle status
    if "status" in data:
        update_kwargs["status"] = data["status"]

    # Handle notes
    if "notes" in data:
        update_kwargs["notes"] = data["notes"]

    service = CommitmentService(session=db.session)

    # Handle timestamp updates (due_at and start_at)
    if "due_at" in data:
        if data["due_at"] is None:
            # Clear due_at using dedicated method
            updated = service.clear_due_at(user_id=user_id, commitment_id=commitment_id)
            if not updated:
                return ("", 404)
        else:
            due_at_local = _parse_datetime(data["due_at"])
            if due_at_local is None:
                return jsonify({"error": "Invalid due_at format. Expected ISO datetime."}), 400
            update_kwargs["due_at"] = due_at_local

    if "start_at" in data:
        if data["start_at"] is None:
            # Clear start_at using dedicated method
            updated = service.clear_start_at(user_id=user_id, commitment_id=commitment_id)
            if not updated:
                return ("", 404)
        else:
            start_at_local = _parse_datetime(data["start_at"])
            if start_at_local is None:
                return jsonify({"error": "Invalid start_at format. Expected ISO datetime."}), 400
            update_kwargs["start_at"] = start_at_local

    try:
        updated = service.update(user_id=user_id, commitment_id=commitment_id, **update_kwargs)
        if not updated:
            return ("", 404)
        return jsonify(updated.as_dict(user_timezone=user_tz))
    except CommitmentValidationError as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def delete_commitments_for_target():
    """
    Delete all commitments for a specific target entity.

    Query parameters:
        target_type (required): Entity type (task, project, routine, session)
        target_id (required): ID of the target entity

    Returns:
        200: Success with count of deleted commitments
        400: If required parameters are missing or invalid
    """
    user_id = int(get_jwt_identity())

    target_type = request.args.get("target_type")
    target_id = request.args.get("target_id")

    # Validate required parameters
    if not target_type:
        return jsonify({"error": "target_type query parameter is required"}), 400
    if not target_id:
        return jsonify({"error": "target_id query parameter is required"}), 400

    try:
        target_id = int(target_id)
    except ValueError:
        return jsonify({"error": "target_id must be an integer"}), 400

    # Delete commitments for target
    service = CommitmentService(session=db.session)
    try:
        deleted = service.delete_for_target(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
        )

        # Return count of deleted commitments
        # Note: service returns boolean, but we'll enhance it to return count
        return jsonify({"deleted": deleted}), 200

    except CommitmentValidationError as e:
        return jsonify({"error": e.message}), 400