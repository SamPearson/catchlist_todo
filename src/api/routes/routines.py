from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import db, Routine, Session, Commitment
from ..utils.helpers import get_current_user_id
from ...config.caldav_client import CalDAVClient
from datetime import datetime, date, timedelta
from ..utils.commitment_utils import create_commitment_from_routine
import random
from ...config.models.tags import Tag, RoutineTag, SessionTag
from dateutil import rrule
import re

routines_bp = Blueprint('routines', __name__)

# Add OPTIONS method handler for CORS preflight requests
@routines_bp.route('/api/routines/import', methods=['OPTIONS'])
def options_routines_import():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

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
        
        # Find the calendar tag (the one that was created during import)
        calendar_tag = None
        for tag_assoc in routine.tag_associations:
            if tag_assoc.tag.name == routine.external_source_name:
                calendar_tag = tag_assoc.tag
                break
        
        result.append({
            'id': routine.id,
            'uid': routine.external_uid,
            'title': routine.title,
            'description': routine.description,
            'rrule': routine.rrule,
            'active': routine.active,
            'external_source': routine.external_source,
            'external_source_name': routine.external_source_name,
            'external_source_color': calendar_tag.color if calendar_tag else '#767676',
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

@routines_bp.route('/api/routines/import', methods=['POST'])
@jwt_required()
def import_routines():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data.get('url') or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
        # Initialize CalDAV client
        client = CalDAVClient(
            url=data['url'],
            username=data['username'],
            password=data['password']
        )
        
        # Get calendars
        calendars = client.get_calendars()
        if not calendars:
            return jsonify({"message": "No calendars found"}), 404
        
        # Get selected calendar
        calendar_index = data.get('calendar_index', 0)
        if calendar_index >= len(calendars):
            return jsonify({"message": "Invalid calendar index"}), 400
        
        selected_calendar = calendars[calendar_index]
        
        # Get events for the specified timeframe
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        events = client.get_events_as_dict(selected_calendar, start_date, end_date)
        
        # Create or get calendar tag
        calendar_tag = Tag.query.filter_by(
            user_id=current_user_id,
            name=selected_calendar.name
        ).first()
        
        if not calendar_tag:
            # Generate a random color for the calendar
            color = f"#{random.randint(0, 0xFFFFFF):06x}"
            calendar_tag = Tag(
                user_id=current_user_id,
                name=selected_calendar.name,
                color=color
            )
            db.session.add(calendar_tag)
            db.session.flush()
        
        imported_count = 0
        
        for event in events:
            try:
                # Check if routine already exists
                existing_routine = Routine.query.filter_by(
                    user_id=current_user_id,
                    external_uid=event['uid']
                ).first()
                
                if existing_routine:
                    continue
                
                # Create new routine
                routine = Routine(
                    user_id=current_user_id,
                    title=event['summary'],
                    description=event.get('description', ''),
                    rrule=event.get('rrule', ''),
                    external_source='caldav',
                    external_uid=event['uid'],
                    external_source_name=selected_calendar.name,  # Store the calendar name
                    active=True
                )
                db.session.add(routine)
                db.session.flush()  # Get the routine ID

                # Associate calendar tag with routine
                routine_tag = RoutineTag(routine_id=routine.id, tag_id=calendar_tag.id)
                db.session.add(routine_tag)

                # Parse RRULE if it exists
                if event.get('rrule'):
                    # Convert RRULE string to rrule object
                    rrule_str = event['rrule']
                    if isinstance(rrule_str, str):
                        # Parse the RRULE string
                        rrule_parts = dict(part.split('=') for part in rrule_str.split(';') if '=' in part)
                        
                        # Create rrule object
                        rule = rrule.rrule(
                            freq=getattr(rrule, rrule_parts.get('FREQ', 'DAILY').upper()),
                            interval=int(rrule_parts.get('INTERVAL', 1)),
                            dtstart=event['start'],
                            until=end_date,
                            byweekday=[getattr(rrule, day) for day in rrule_parts.get('BYDAY', '').split(',')] if 'BYDAY' in rrule_parts else None
                        )
                        
                        # Get all occurrences within the timeframe
                        occurrences = list(rule.between(start_date, end_date, inc=True))
                    else:
                        # If RRULE is not a string, just use the start date
                        occurrences = [event['start']]
                else:
                    # For non-recurring events, just use the start date
                    occurrences = [event['start']]

                # Create sessions for each occurrence
                for occurrence in occurrences:
                    # Create session
                    session_start = datetime.combine(occurrence.date(), event['start'].time())
                    session_end = datetime.combine(occurrence.date(), event['end'].time())
                    
                    session = Session(
                        routine_id=routine.id,
                        start_time=session_start,
                        end_time=session_end,
                        user_id=current_user_id
                    )
                    db.session.add(session)
                    db.session.flush()  # Get the session ID

                    # Associate calendar tag with session
                    session_tag = SessionTag(session_id=session.id, tag_id=calendar_tag.id)
                    db.session.add(session_tag)

                    # Create commitment for the session
                    commitment = Commitment(
                        user_id=current_user_id,
                        due_date=occurrence.date(),
                        start_time=session_start,
                        end_time=session_end,
                        routine_id=routine.id,
                        session_id=session.id
                    )
                    db.session.add(commitment)

                imported_count += 1
            except Exception as e:
                print(f"Error importing event: {str(e)}")
                continue
        
        db.session.commit()
        return jsonify({"success": True, "imported_count": imported_count})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

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