from datetime import datetime, time
from zoneinfo import ZoneInfo

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.db import db
from src.database.timeframes.service import TimeframeService, validate_kind, SUPPORTED_KINDS, UnsupportedTimeframeKind
from src.database.users.models import User


def _parse_local_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def _validate_timezone(tz: str) -> str | None:
    try:
        ZoneInfo(tz)
        return None
    except Exception:
        return f"Invalid timezone '{tz}'. Expected an IANA timezone like 'America/Chicago'."


def _get_user_timezone(user_id: int) -> str:
    user = User.query.get(user_id)
    if user and getattr(user, "timezone", None):
        return user.timezone
    return "UTC"


def _get_tz_or_user_default(user_id: int) -> str:
    tz = request.args.get("tz")
    if tz:
        return tz
    return _get_user_timezone(user_id)


def _today_in_tz(tz: str):
    return datetime.now(ZoneInfo(tz)).date()


def _local_date_window_to_utc(start_day, end_day, tz: str):
    """
    Convert local date window [start_day, end_day] to UTC instants covering full days.
    We treat it as half-open: [start_local_midnight, end_local_midnight)
    """
    zone = ZoneInfo(tz)
    utc = ZoneInfo("UTC")
    start_local = datetime.combine(start_day, time.min, tzinfo=zone)
    end_local = datetime.combine(end_day, time.min, tzinfo=zone)
    return start_local.astimezone(utc), end_local.astimezone(utc)


@jwt_required()
def list_timeframe_kinds():
    return jsonify({"kinds": sorted(SUPPORTED_KINDS), "default_tz": "UTC"})


@jwt_required()
def list_timeframes():
    user_id = int(get_jwt_identity())

    kind = request.args.get("kind")
    if kind:
        kind_error = validate_kind(kind)
        if kind_error:
            return jsonify({"error": kind_error}), 400
        kind = kind.strip().lower()

    user_tz = request.args.get("tz", "UTC")
    tz_error = _validate_timezone(user_tz)
    if tz_error:
        return jsonify({"error": tz_error}), 400
    
    # If no explicit tz provided, use user's default
    if not request.args.get("tz"):
        user_tz = _get_user_timezone(user_id)

    start_str = request.args.get("start")
    end_str = request.args.get("end")

    service = TimeframeService(session=db.session)

    if start_str and end_str:
        start_day = _parse_local_date(start_str)
        end_day = _parse_local_date(end_str)
        if start_day is None or end_day is None:
            return jsonify({"error": "Invalid start/end date format. Expected YYYY-MM-DD."}), 400
        if end_day < start_day:
            return jsonify({"error": "end must be on or after start."}), 400

        start_utc, end_utc = _local_date_window_to_utc(start_day, end_day, user_tz)

        if not kind:
            return jsonify({"error": "kind is required when using start/end window queries."}), 400

        items = service.repo.list_overlapping(
            user_id=user_id,
            kind=kind,
            start_utc=start_utc,
            end_utc=end_utc,
        )
        return jsonify([tf.as_dict(user_timezone=user_tz) for tf in items])

    if kind:
        items = service.repo.list_for_user(user_id=user_id, kind=kind)
    else:
        items = service.repo.list_for_user(user_id=user_id)

    return jsonify([tf.as_dict(user_timezone=user_tz) for tf in items])


@jwt_required()
def create_timeframe():
    """
    Create a timeframe via get-or-create semantics.

    Body:
      {
        "kind": "day|week|month|season|year",
        "date": "YYYY-MM-DD" (optional; defaults to today in tz),
        "tz": "America/Chicago" (optional; defaults to user's timezone)
      }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    kind = (data.get("kind") or "").strip().lower()
    kind_error = validate_kind(kind)
    if kind_error:
        return jsonify({"error": kind_error}), 400

    user_tz = data.get("tz") or _get_user_timezone(user_id)
    tz_error = _validate_timezone(user_tz)
    if tz_error:
        return jsonify({"error": tz_error}), 400

    date_str = data.get("date")
    if date_str:
        local_day = _parse_local_date(date_str)
        if local_day is None:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400
    else:
        local_day = _today_in_tz(user_tz)

    service = TimeframeService(session=db.session)
    try:
        tf = service.get_or_create_for_date(
            user_id=user_id,
            kind=kind,
            local_date=local_day,
            timezone=user_tz,
        )
    except UnsupportedTimeframeKind as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(tf.as_dict()), 201


@jwt_required()
def get_timeframe_by_id(timeframe_id: int):
    user_id = int(get_jwt_identity())
    user_tz = _get_user_timezone(user_id)
    service = TimeframeService(session=db.session)
    tf = service.get_timeframe(timeframe_id, user_id=user_id)
    return jsonify(tf.as_dict(user_timezone=user_tz)) if tf else ("", 404)


@jwt_required()
def get_timeframe_today(kind: str):
    user_id = int(get_jwt_identity())

    kind_error = validate_kind(kind)
    if kind_error:
        return jsonify({"error": kind_error}), 400

    user_tz = _get_tz_or_user_default(user_id)
    tz_error = _validate_timezone(user_tz)
    if tz_error:
        return jsonify({"error": tz_error}), 400

    local_day = _today_in_tz(user_tz)

    service = TimeframeService(session=db.session)
    try:
        tf = service.get_or_create_for_date(
            user_id=user_id,
            kind=kind,
            local_date=local_day,
            timezone=user_tz,
        )
        return jsonify(tf.as_dict(user_timezone=user_tz))
    except UnsupportedTimeframeKind as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@jwt_required()
def get_timeframe(kind: str, date: str):
    user_id = int(get_jwt_identity())

    kind_error = validate_kind(kind)
    if kind_error:
        return jsonify({"error": kind_error}), 400

    local_day = _parse_local_date(date)
    if local_day is None:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

    user_tz = _get_tz_or_user_default(user_id)
    tz_error = _validate_timezone(user_tz)
    if tz_error:
        return jsonify({"error": tz_error}), 400

    service = TimeframeService(session=db.session)
    try:
        tf = service.get_or_create_for_date(
            user_id=user_id,
            kind=kind,
            local_date=local_day,
            timezone=user_tz,
        )
        return jsonify(tf.as_dict(user_timezone=user_tz))
    except UnsupportedTimeframeKind as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


