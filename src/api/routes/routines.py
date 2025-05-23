from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import db, Routine, Session, Commitment, Calendar
from ..utils.helpers import get_current_user_id
from ...config.caldav_client import CalDAVClient, CalDAVError, CalDAVConnectionError
from datetime import datetime, date, timedelta
from ..utils.commitment_utils import create_commitment_from_routine
import random
from ...config.models.tags import Tag, RoutineTag, SessionTag
from dateutil import rrule
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
import pytz

routines_bp = Blueprint('routines', __name__)

logger = logging.getLogger(__name__)

@dataclass
class TimeframeRange:
    start: datetime
    end: datetime

def get_timeframe_range(timeframe: str, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> TimeframeRange:
    """Calculate the date range for a given timeframe"""
    now = datetime.now()
    
    if timeframe == 'custom' and start_date and end_date:
        return TimeframeRange(
            start=datetime.fromisoformat(start_date),
            end=datetime.fromisoformat(end_date)
        )
    
    if timeframe == 'day':
        return TimeframeRange(
            start=now.replace(hour=0, minute=0, second=0, microsecond=0),
            end=now.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
    
    if timeframe == 'week':
        # Get start of week (Monday)
        start = now - timedelta(days=now.weekday())
        return TimeframeRange(
            start=start.replace(hour=0, minute=0, second=0, microsecond=0),
            end=(start + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
        )
    
    if timeframe == 'month':
        return TimeframeRange(
            start=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            end=(now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        )
    
    if timeframe == 'season':
        # Define seasons
        seasons = [
            (3, 5),   # Spring (Mar-May)
            (6, 8),   # Summer (Jun-Aug)
            (9, 11),  # Fall (Sep-Nov)
            (12, 2)   # Winter (Dec-Feb)
        ]
        
        current_month = now.month
        current_season = next(
            (start, end) for start, end in seasons 
            if start <= current_month <= end
        )
        
        if current_month >= current_season[0]:
            year = now.year
        else:
            year = now.year - 1
            
        start = datetime(year, current_season[0], 1)
        if current_season[1] == 2:
            end = datetime(year + 1, 3, 1) - timedelta(days=1)
        else:
            end = datetime(year, current_season[1] + 1, 1) - timedelta(days=1)
            
        return TimeframeRange(start=start, end=end)
    
    if timeframe == 'year':
        return TimeframeRange(
            start=now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            end=now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        )
    
    # Default to one year
    return TimeframeRange(
        start=now,
        end=now + timedelta(days=365)
    )

@routines_bp.route('/api/caldav/test-connection', methods=['POST'])
@jwt_required()
def test_caldav_connection():
    """Test CalDAV connection and return available calendars"""
    data = request.get_json()
    
    if not data or not data.get('url') or not data.get('username') or not data.get('password'):
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400
    
    try:
        client = CalDAVClient(
            url=data['url'],
            username=data['username'],
            password=data['password']
        )
        
        if not client.connect():
            return jsonify({
                "success": False,
                "message": "Failed to connect to CalDAV server"
            }), 400
        
        calendars = client.get_calendars()
        logger.debug(f"Retrieved {len(calendars)} calendars")
        
        # Convert calendars to a list of dictionaries
        calendar_list = []
        for cal in calendars:
            try:
                calendar_list.append({
                    "name": str(cal.name),
                    "color": str(cal.color),
                    "url": str(cal.url),
                    "uid": str(cal.uid)
                })
            except Exception as e:
                logger.error(f"Error processing calendar: {str(e)}")
                continue
        
        logger.debug(f"Successfully processed {len(calendar_list)} calendars")
        
        return jsonify({
            "success": True,
            "calendars": calendar_list
        })
        
    except CalDAVConnectionError as e:
        logger.error(f"CalDAV connection error: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except CalDAVError as e:
        logger.error(f"CalDAV error: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error in test_caldav_connection: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }), 500

def generate_random_color():
    """Generate a random hex color code"""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

@routines_bp.route('/api/routines/import', methods=['POST'])
@jwt_required()
def import_routines():
    """Import routines from CalDAV calendars"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('url') or not data.get('username') or not data.get('password'):
            return jsonify({
                "success": False,
                "message": "Missing required fields"
            }), 400
            
        # Initialize CalDAV client
        client = CalDAVClient(
            url=data['url'],
            username=data['username'],
            password=data['password']
        )
        
        # Connect to CalDAV server
        if not client.connect():
            return jsonify({
                "success": False,
                "message": "Failed to connect to CalDAV server"
            }), 400
        
        # Get calendars
        calendars = client.get_calendars()
        
        # Filter calendars if indices are provided
        if data.get('calendar_indices'):
            calendars = [calendars[i] for i in data['calendar_indices'] if i < len(calendars)]
        
        imported_count = 0
        
        for calendar in calendars:
            # Create or get calendar object
            calendar_obj = Calendar.query.filter_by(
                user_id=user_id,
                external_uid=calendar.uid
            ).first()
            
            if not calendar_obj:
                calendar_obj = Calendar(
                    name=calendar.name,
                    color=calendar.color,
                    user_id=user_id,
                    external_uid=calendar.uid,
                    external_source='caldav'
                )
                db.session.add(calendar_obj)
                db.session.flush()
            
            # Create or get calendar tag
            calendar_tag = Tag.query.filter_by(
                name=calendar.name,
                user_id=user_id
            ).first()
            
            if not calendar_tag:
                calendar_tag = Tag(
                    name=calendar.name,
                    color=generate_random_color(),  # Use random color instead of calendar color
                    user_id=user_id
                )
                db.session.add(calendar_tag)
                db.session.flush()
            
            # Get events from calendar
            events = client.get_events(calendar.url)
            
            for event in events:
                # Skip if no RRULE
                if not event.rrule:
                    continue
                    
                # Skip if already imported
                existing_routine = Routine.query.filter_by(
                    external_uid=event.uid,
                    user_id=user_id
                ).first()
                
                if existing_routine:
                    continue
                
                # Use the timezone from the event
                timezone = event.timezone
                logger.debug(f"Using timezone for event {event.summary}: {timezone}")
                
                # Create routine
                routine = Routine(
                    title=event.summary,
                    description=event.description,
                    rrule=event.rrule,
                    active=True,
                    user_id=user_id,
                    calendar_id=calendar_obj.id,  # Set the calendar_id
                    external_uid=event.uid,
                    external_source='caldav',
                    external_source_name=calendar.name,
                    timezone=timezone
                )
                
                db.session.add(routine)
                db.session.flush()
                
                # Create initial session from the event
                session = Session(
                    routine_id=routine.id,
                    start_time=event.start,
                    end_time=event.end,
                    user_id=user_id,
                    timezone=timezone
                )
                db.session.add(session)
                db.session.flush()
                
                # Create initial commitment for the session
                commitment = Commitment(
                    user_id=user_id,
                    session_id=session.id,
                    routine_id=routine.id,
                    due_date=event.start.date(),
                    start_time=event.start,
                    end_time=event.end
                )
                db.session.add(commitment)
                
                # Associate routine with calendar tag
                routine_tag = RoutineTag(
                    routine_id=routine.id,
                    tag_id=calendar_tag.id
                )
                db.session.add(routine_tag)
                
                imported_count += 1
        
        db.session.commit()
        logger.info(f"Successfully imported {imported_count} routines")
        return jsonify({
            "success": True,
            "imported_count": imported_count
        })
        
    except CalDAVConnectionError as e:
        db.session.rollback()
        logger.error(f"CalDAV connection error: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except CalDAVError as e:
        db.session.rollback()
        logger.error(f"CalDAV error: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in import_routines: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }), 500

@routines_bp.route('/api/routines', methods=['GET'])
@jwt_required()
def get_routines():
    current_user_id = get_current_user_id()
    routines = Routine.query.filter_by(user_id=current_user_id).all()
    
    result = []
    for routine in routines:
        # Get the next session for this routine
        next_session = Session.query.filter(
            Session.routine_id == routine.id,
            Session.start_time >= datetime.now()
        ).order_by(Session.start_time.asc()).first()
        
        # Get the calendar information
        calendar = routine.calendar
        calendar_info = None
        if calendar:
            calendar_info = {
                'id': calendar.id,
                'name': calendar.name,
                'color': calendar.color
            }
        
        result.append({
            'id': routine.id,
            'uid': routine.external_uid,
            'title': routine.title,
            'description': routine.description,
            'rrule': routine.rrule,
            'active': routine.active,
            'external_source': routine.external_source,
            'external_source_name': routine.external_source_name,
            'calendar': calendar_info,
            'start_time': next_session.start_time.strftime('%H:%M') if next_session else None,
            'end_time': next_session.end_time.strftime('%H:%M') if next_session else None,
            'tags': [assoc.tag.as_dict() for assoc in routine.tag_associations]
        })
    
    return jsonify(result)

@routines_bp.route('/api/routines', methods=['POST'])
@jwt_required()
def create_routine():
    """Create a new routine"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({"message": "Title is required"}), 400
    
    try:
        routine = Routine(
            title=data.get('title'),
            description=data.get('description'),
            rrule=data.get('rrule'),
            active=True,
            user_id=user_id
        )
        
        db.session.add(routine)
        db.session.flush()  # Get the routine ID
        
        # Create sessions if timeframe is provided
        if data.get('start_date') and data.get('end_date'):
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            
            # If start_time and end_time are provided, use them for all sessions
            start_time = None
            end_time = None
            if data.get('start_time') and data.get('end_time'):
                start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            
            # Create sessions for each day in the timeframe
            current_date = start_date
            while current_date <= end_date:
                # Create session
                session_start = datetime.combine(current_date, start_time) if start_time else datetime.combine(current_date, datetime.min.time())
                session_end = datetime.combine(current_date, end_time) if end_time else datetime.combine(current_date, datetime.max.time())
                
                session = Session(
                    routine_id=routine.id,
                    start_time=session_start,
                    end_time=session_end,
                    user_id=user_id
                )
                db.session.add(session)
                db.session.flush()  # Get the session ID
                
                # Create commitment for the session
                commitment = Commitment(
                    user_id=user_id,
                    due_date=current_date,
                    start_time=session_start,
                    end_time=session_end,
                    routine_id=routine.id,
                    session_id=session.id
                )
                db.session.add(commitment)
                
                # Move to next day
                current_date += timedelta(days=1)
        
        db.session.commit()
        return jsonify(routine.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/<int:routine_id>', methods=['PUT'])
@jwt_required()
def update_routine(routine_id):
    """Update a routine"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    routine = Routine.query.filter_by(id=routine_id, user_id=user_id).first()
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
    
    try:
        # Update routine fields
        if 'title' in data:
            routine.title = data['title']
        if 'description' in data:
            routine.description = data['description']
        if 'rrule' in data:
            routine.rrule = data['rrule']
        if 'active' in data:
            routine.active = data['active']
            
            # Update related commitments based on active status
            if not routine.active:
                # Deactivate all future commitments
                future_commitments = Commitment.query.filter(
                    Commitment.routine_id == routine.id,
                    Commitment.due_date >= date.today()
                ).all()
                
                for commitment in future_commitments:
                    commitment.completed = True  # Mark as completed to hide from active commitments
            else:
                # Reactivate all future commitments
                future_commitments = Commitment.query.filter(
                    Commitment.routine_id == routine.id,
                    Commitment.due_date >= date.today()
                ).all()
                
                for commitment in future_commitments:
                    commitment.completed = False  # Mark as not completed to show in active commitments
        
        db.session.commit()
        return jsonify(routine.as_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/<int:routine_id>', methods=['DELETE'])
@jwt_required()
def delete_routine(routine_id):
    current_user_id = get_current_user_id()
    routine = Routine.query.filter_by(id=routine_id, user_id=current_user_id).first()
    
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
    
    try:
        db.session.delete(routine)
        db.session.commit()
        return jsonify({"message": "Routine deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

def random_color():
    return "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

@routines_bp.route('/api/routines/<int:routine_id>/sessions', methods=['GET'])
@jwt_required()
def get_routine_sessions(routine_id):
    current_user_id = get_current_user_id()
    routine = Routine.query.filter_by(id=routine_id, user_id=current_user_id).first()
    
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
        
    sessions = Session.query.filter_by(routine_id=routine_id).order_by(Session.start_time.desc()).all()
    
    result = []
    for session in sessions:
        result.append({
            'id': session.id,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat(),
            'completed': session.completed,
            'rpe': session.rpe,
            'notes': session.notes,
            'tags': [assoc.tag.as_dict() for assoc in session.tag_associations]
        })
        
    return jsonify(result)

@routines_bp.route('/api/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_session(session_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    # Find session and verify it belongs to the current user
    session = Session.query.join(Routine).filter(
        Session.id == session_id,
        Routine.user_id == current_user_id
    ).first()
    
    if not session:
        return jsonify({"message": "Session not found"}), 404
        
    try:
        if 'completed' in data:
            session.completed = data.get('completed')
        if 'rpe' in data:
            session.rpe = data.get('rpe')
        if 'notes' in data:
            session.notes = data.get('notes')
            
        db.session.commit()
        
        result = {
            'id': session.id,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat(),
            'completed': session.completed,
            'rpe': session.rpe,
            'notes': session.notes,
            'tags': [assoc.tag.as_dict() for assoc in session.tag_associations]
        }
        
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/<int:routine_id>/toggle-active', methods=['PUT'])
@jwt_required()
def toggle_routine_active(routine_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if 'active' not in data:
        return jsonify({"message": "Active state is required"}), 400
    
    routine = Routine.query.filter_by(id=routine_id, user_id=current_user_id).first()
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
    
    try:
        routine.active = data.get('active')
        db.session.commit()
        
        return jsonify({
            'id': routine.id,
            'title': routine.title,
            'active': routine.active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/today', methods=['GET'])
@jwt_required()
def get_today_routines():
    current_user_id = get_current_user_id()
    today = date.today()
    
    # Get all sessions for today
    sessions = Session.query.join(Routine).filter(
        Session.user_id == current_user_id,
        db.func.date(Session.start_time) == today
    ).order_by(Session.start_time.asc()).all()
    
    result = []
    for session in sessions:
        routine = session.routine
        result.append({
            'id': session.id,
            'routine_id': routine.id,
            'title': routine.title,
            'description': routine.description,
            'start_time': session.start_time.strftime('%H:%M'),
            'end_time': session.end_time.strftime('%H:%M'),
            'completed': session.completed,
            'rpe': session.rpe,
            'notes': session.notes
        })
    
    return jsonify(result)

@routines_bp.route('/api/routines/range', methods=['GET'])
@jwt_required()
def get_routines_range():
    """Get routines within a date range"""
    current_user_id = get_current_user_id()
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({"message": "Start date and end date are required"}), 400
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get all sessions within the date range
    sessions = Session.query.join(Routine).filter(
        Session.user_id == current_user_id,
        db.func.date(Session.start_time).between(start_date, end_date),
        Routine.active == True
    ).order_by(Session.start_time.asc()).all()
    
    result = []
    for session in sessions:
        routine = session.routine
        result.append({
            'id': session.id,
            'routine_id': routine.id,
            'title': routine.title,
            'start_time': session.start_time.strftime('%H:%M') if session.start_time else None,
            'end_time': session.end_time.strftime('%H:%M') if session.end_time else None,
            'description': routine.description,
            'completed': session.completed,
            'rpe': session.rpe,
            'notes': session.notes,
            'is_all_day': ((session.start_time.strftime('%H:%M') if session.start_time else None) == '00:00' and
                          (session.end_time.strftime('%H:%M') if session.end_time else None) == '00:00')
        })
    
    return jsonify(result)

@routines_bp.route('/api/routines/<int:routine_id>/create-sessions', methods=['POST'])
@jwt_required()
def create_routine_sessions(routine_id):
    """Create sessions for a routine within a specified timeframe"""
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    # Verify routine exists and belongs to user
    routine = Routine.query.filter_by(id=routine_id, user_id=current_user_id).first()
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
    
    if not data or not data.get('start_date') or not data.get('end_date'):
        return jsonify({"message": "Start date and end date are required"}), 400
    
    try:
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Get the routine's timezone
        timezone = routine.timezone or 'America/Chicago'
        tz = pytz.timezone(timezone)
        logger.debug(f"Using timezone for sessions: {timezone}")
        
        # Get the first session to use as a template
        first_session = Session.query.filter_by(routine_id=routine_id).order_by(Session.start_time).first()
        if not first_session:
            return jsonify({"error": "No existing session found for this routine"}), 400
        
        # Get the time components from the first session in UTC
        start_time = first_session.start_time.time()
        end_time = first_session.end_time.time()
        logger.debug(f"First session start time (UTC): {start_time}")
        logger.debug(f"First session end time (UTC): {end_time}")
        
        # Create timezone-aware datetime objects for the start and end times
        start_dt = datetime.combine(start_date, start_time)
        end_dt = datetime.combine(end_date, end_time)
        
        # Localize the datetimes to the routine's timezone
        start_dt = tz.localize(start_dt)
        end_dt = tz.localize(end_dt)
        
        logger.debug(f"New session start time (localized): {start_dt}")
        logger.debug(f"New session end time (localized): {end_dt}")
        
        # Parse RRULE
        if not routine.rrule:
            return jsonify({"message": "Routine has no recurrence rule"}), 400
        
        # Parse RRULE with timezone-aware start time
        rule = rrule.rrulestr(routine.rrule, dtstart=start_dt)
        
        # Generate sessions
        session_count = 0
        commitment_count = 0
        for dt in rule.between(start_dt, end_dt):
            # Ensure dt is timezone-aware
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            
            # Calculate end time using the duration from the first session
            duration = first_session.end_time - first_session.start_time
            end_time = dt + duration
            
            # Check if session already exists
            existing_session = Session.query.filter_by(
                routine_id=routine.id,
                start_time=dt
            ).first()
            
            if existing_session:
                continue
            
            # Create session
            session = Session(
                routine_id=routine.id,
                start_time=dt,
                end_time=end_time,
                user_id=current_user_id,
                timezone=timezone
            )
            db.session.add(session)
            db.session.flush()  # Get the session ID
            session_count += 1
            
            # Create commitment for the session
            commitment = Commitment(
                user_id=current_user_id,
                due_date=dt.date(),
                start_time=dt,
                end_time=end_time,
                routine_id=routine.id,
                session_id=session.id,
                title=routine.title,
                description=routine.description
            )
            db.session.add(commitment)
            commitment_count += 1
        
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Created {session_count} sessions and {commitment_count} commitments",
            "session_count": session_count,
            "commitment_count": commitment_count
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating sessions: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error creating sessions: {str(e)}"
        }), 500 