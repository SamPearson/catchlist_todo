import logging
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.base.exceptions import EntityNotFoundError
from src.database.db import db
from src.database.routines.service import RoutineService, RoutineValidationError
from src.database.sessions.service import SessionService
from src.api.utils.caldav_client import CalDAVClient
from src.database.users.models import User

# Import the timezone utilities
from src.utils.timezone import parse_dt, to_utc, from_utc, localize_dict


def get_user_timezone(user_id):
    """Get the user's timezone or return UTC as default"""
    user = User.query.get(user_id)
    return user.timezone if user and hasattr(user, 'timezone') and user.timezone else "UTC"


@jwt_required()
def list_routines():
    user_id = int(get_jwt_identity())
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    service = RoutineService(db.session)
    items = service.list_routines(user_id, active_only=active_only)

    # Get user timezone
    user_timezone = get_user_timezone(user_id)

    # Convert routines to dicts and localize timestamps
    routine_dicts = []
    for routine in items:
        routine_dict = routine.as_dict()
        # Only datetime fields will be converted, time-of-day fields pass through
        localized = localize_dict(routine_dict, user_timezone)
        routine_dicts.append(localized)

    return jsonify(routine_dicts)


@jwt_required()
def get_routine(routine_id: int):
    user_id = int(get_jwt_identity())
    service = RoutineService(db.session)
    routine = service.get_routine(routine_id, user_id)

    if not routine:
        return jsonify({'error': f'Routine {routine_id} not found'}), 404

    # Convert routine to dict and localize timestamps
    routine_dict = routine.as_dict()
    routine_timezone = routine_dict.get('timezone') or "UTC"
    localized = localize_dict(routine_dict, routine_timezone)

    return jsonify(localized)


@jwt_required()
def create_routine():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = RoutineService(db.session)

    if data.get('external_uid') or data.get('external_source') or data.get('external_source_name'):
        return jsonify({"error": "Cannot set external_uid, external_source or external_source_name manually."
                                 "If this routine is connect to an external calendar, "
                                 "create it with the sync calendar endpoint instead."}), 400


    try:
        routine = service.create_routine(user_id, data)

        # Get user timezone and localize the response
        user_timezone = get_user_timezone(user_id)
        routine_dict = routine.as_dict()
        localized = localize_dict(routine_dict, user_timezone)

        return jsonify(localized), 201
    except RoutineValidationError as e:
        return jsonify({"error": str(e)}), 400


@jwt_required()
def update_routine(routine_id: int):
    """PATCH /api/routines/{id} - Update routine with optional cascade to sessions"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = RoutineService(db.session)

    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    # Check for disallowed fields
    disallowed_fields = {'id', 'user_id', 'created_at', 'updated_at', 'calendar_id', 'external_uid', 'external_source',
                         'external_source_name'}
    if any(field in data for field in disallowed_fields):
        return jsonify({
            'error': 'Cannot update read-only fields (id, user_id, created_at, updated_at, calendar_id, external_*). '
                     'Use DELETE /api/routines/{id}/sessions/{future|past} to manage sessions.'
        }), 400

    try:
        # Parse cascade parameters (default: both false for safety)
        cascade_future = request.args.get('cascade_future', 'false').lower() == 'true'
        cascade_past = request.args.get('cascade_past', 'false').lower() == 'true'

        updated = service.update_routine(
            routine_id,
            user_id,
            data,
            cascade_future=cascade_future,
            cascade_past=cascade_past
        )

        # Get user timezone and localize the response
        user_timezone = get_user_timezone(user_id)
        routine_dict = updated.as_dict()
        localized = localize_dict(routine_dict, user_timezone)

        return jsonify(localized)
    except EntityNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except RoutineValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in update_routine: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@jwt_required()
def delete_routine(routine_id: int):
    user_id = int(get_jwt_identity())
    service = RoutineService(db.session)

    try:
        service.delete_routine(routine_id, user_id)
        return ('', 204)
    except EntityNotFoundError as e:
        return jsonify({"error": str(e)}), 404

@jwt_required()
def delete_future_sessions(routine_id: int):
    """DELETE /api/routines/{id}/sessions/future - Delete future sessions for a routine"""
    user_id = int(get_jwt_identity())
    service = RoutineService(db.session)

    try:
        # Parse parameters
        incomplete_only = request.args.get('incomplete_only', 'true').lower() == 'true'

        routine = service.get_routine(routine_id, user_id)
        if not routine:
            return '', 404

        deleted_count = service.delete_future_sessions(
            routine_id,
            user_id,
            incomplete_only=incomplete_only
        )

        return jsonify({
            'message': f'Deleted {deleted_count} future sessions',
            'deleted_count': deleted_count
        }), 200
    except Exception as e:
        logging.error(f"Error deleting future sessions: {str(e)}")
        return jsonify({"error": str(e)}), 500


@jwt_required()
def delete_past_sessions(routine_id: int):
    """DELETE /api/routines/{id}/sessions/past - Delete past sessions for a routine"""
    user_id = int(get_jwt_identity())
    service = RoutineService(db.session)

    try:
        # Parse parameters
        incomplete_only = request.args.get('incomplete_only', 'true').lower() == 'true'

        routine = service.get_routine(routine_id, user_id)
        if not routine:
            return jsonify({'error': f'Routine {routine_id} not found'}), 404

        # Get past sessions and delete them
        if incomplete_only:
            sessions_to_delete = [s for s in service.get_past_sessions(routine_id, user_id)
                                  if s.status == 'scheduled']
        else:
            sessions_to_delete = service.get_past_sessions(routine_id, user_id)

        deleted_count = 0
        for session in sessions_to_delete:
            if service.session_repo.delete(session):
                deleted_count += 1

        logging.info(f"Deleted {deleted_count} past sessions for routine {routine_id}")

        return jsonify({
            'message': f'Deleted {deleted_count} past sessions',
            'deleted_count': deleted_count
        }), 200
    except Exception as e:
        logging.error(f"Error deleting past sessions: {str(e)}")
        return jsonify({"error": str(e)}), 500




@jwt_required()
def generate_routine_sessions(routine_id: int):
    """Generate sessions for a routine based on its recurrence rule for a specified period"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if 'start_date' not in data or 'end_date' not in data:
        return jsonify({"error": "start_date and end_date are required"}), 400

    try:
        service = RoutineService(db.session)
        
        # Get user timezone
        user_timezone = get_user_timezone(user_id)
        
        # Parse dates (assuming ISO format)
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])

        # If end_date is just a date (no time), set it to end of day
        if len(data['end_date']) <= 10:  # Just YYYY-MM-DD
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Parse inheritance parameters (default: both true)
        inherit_tags = data.get('inherit_tags', True)
        inherit_principles = data.get('inherit_principles', True)

        session_service = SessionService(db.session)
        sessions = session_service.create_sessions_for_period(
            user_id,
            routine_id,
            start_date,
            end_date,
            inherit_tags=inherit_tags,
            inherit_principles=inherit_principles
        )
        
        # Convert sessions to dicts for response
        session_dicts = [session.as_dict() for session in sessions]
        
        return jsonify(session_dicts), 201

    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}. Use ISO format: YYYY-MM-DD or YYYY-MM-DDThh:mm:ss"}), 400
    except RoutineValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in generate_routine_sessions: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500