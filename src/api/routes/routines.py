from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import db, CalendarEvent, EventExecution, Routine, Session, Commitment
from ..utils.helpers import get_current_user_id
from ...config.caldav_client import CalDAVClient
from datetime import datetime, date, timedelta
from ..utils.commitment_utils import create_commitment_from_routine

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
        
        result.append({
            'id': routine.id,
            'uid': routine.external_uid,
            'summary': routine.title,
            'description': routine.description,
            'rrule': routine.rrule,
            'active': routine.active,
            'external_source': routine.external_source,
            'start_time': next_session.start_time.strftime('%H:%M') if next_session else None,
            'end_time': next_session.end_time.strftime('%H:%M') if next_session else None
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
        db.session.commit()
        
        # Create a session for today if start_time and end_time are provided
        if data.get('start_time') and data.get('end_time'):
            start_time = datetime.strptime(data.get('start_time'), '%H:%M')
            end_time = datetime.strptime(data.get('end_time'), '%H:%M')
            
            # Set the date to today
            today = date.today()
            start_time = datetime.combine(today, start_time.time())
            end_time = datetime.combine(today, end_time.time())
            
            session = Session(
                routine_id=routine.id,
                start_time=start_time,
                end_time=end_time,
                user_id=user_id
            )
            
            db.session.add(session)
            db.session.commit()
            
            # Create a commitment for the session
            create_commitment_from_routine(routine, session, user_id)
        
        return jsonify(routine.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_routine(event_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user_id).first()
    if not event:
        return jsonify({"message": "Event not found"}), 404
    
    try:
        if 'summary' in data:
            event.summary = data.get('summary')
        if 'description' in data:
            event.description = data.get('description')
        if 'start_time' in data:
            event.start_time = datetime.strptime(data.get('start_time'), '%H:%M')
        if 'end_time' in data:
            event.end_time = datetime.strptime(data.get('end_time'), '%H:%M')
        if 'rrule' in data:
            event.rrule = data.get('rrule')
        
        db.session.commit()
        
        result = {
            'id': event.id,
            'uid': event.uid,
            'summary': event.summary,
            'description': event.description,
            'start_time': event.start_time.strftime('%H:%M'),
            'end_time': event.end_time.strftime('%H:%M'),
            'rrule': event.rrule
        }
        
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_routine(event_id):
    current_user_id = get_current_user_id()
    event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user_id).first()
    
    if not event:
        return jsonify({"message": "Event not found"}), 404
    
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Event deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/import', methods=['POST'])
@jwt_required()
def import_caldav_events():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('url'):
        return jsonify({"message": "CalDAV URL is required"}), 400
    
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')
    
    caldav_client = CalDAVClient(url, username, password)
    
    if not caldav_client.connect():
        return jsonify({"success": False, "message": "Failed to connect to CalDAV server"}), 400
        
    calendars = caldav_client.get_calendars()
    if not calendars:
        return jsonify({"success": False, "message": "No calendars found"}), 400
        
    # Use the first calendar for simplicity
    first_calendar = calendars[0]
    events = caldav_client.get_events_as_dict(first_calendar)
    
    if not events:
        return jsonify({"success": True, "message": "No events found to import", "imported_count": 0})
    
    # Import events to database
    imported_count = 0
    for event_dict in events:
        # Skip events without required fields
        if not event_dict.get('uid') or not event_dict.get('summary') or not event_dict.get('start') or not event_dict.get('end'):
            continue
            
        # Check if routine already exists to avoid duplicates
        existing_routine = Routine.query.filter_by(external_uid=event_dict['uid'], user_id=current_user_id).first()
        if existing_routine:
            continue
            
        try:
            # Create the routine
            routine = Routine(
                title=event_dict['summary'],
                description=event_dict.get('description', ''),
                rrule=event_dict.get('rrule', ''),
                active=True,
                user_id=current_user_id,
                external_uid=event_dict['uid'],
                external_source='caldav'
            )
            db.session.add(routine)
            db.session.flush()  # Get the routine ID
            
            # Create sessions for the next 90 days
            start_date = datetime.now()
            end_date = start_date + timedelta(days=90)
            
            # Parse RRULE to get recurring dates
            if event_dict.get('rrule'):
                # Use dateutil.rrule to parse the RRULE string
                from dateutil.rrule import rrulestr
                from dateutil.parser import parse
                
                rrule_str = event_dict['rrule']
                if 'DTSTART' not in rrule_str:
                    # Add DTSTART if not present
                    rrule_str = f"DTSTART:{event_dict['start'].strftime('%Y%m%dT%H%M%S')}\n{rrule_str}"
                
                rule = rrulestr(rrule_str)
                dates = list(rule.between(start_date, end_date))
            else:
                # Single event
                dates = [event_dict['start']]
            
            # Create sessions and commitments for each date
            for date in dates:
                session = Session(
                    routine_id=routine.id,
                    start_time=date,
                    end_time=date + (event_dict['end'] - event_dict['start']),
                    user_id=current_user_id
                )
                db.session.add(session)
                db.session.flush()  # Get the session ID
                
                # Create commitment for this session
                create_commitment_from_routine(routine, session, current_user_id)
            
            imported_count += 1
            
        except Exception as e:
            print(f"Error importing event: {str(e)}")
            continue
            
    try:
        db.session.commit()
        return jsonify({
            "success": True, 
            "message": f"Successfully imported {imported_count} routines", 
            "imported_count": imported_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error saving imported routines: {str(e)}"}), 500

@routines_bp.route('/api/routines/<int:event_id>/executions', methods=['GET'])
@jwt_required()
def get_event_executions(event_id):
    current_user_id = get_current_user_id()
    event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user_id).first()
    
    if not event:
        return jsonify({"message": "Event not found"}), 404
        
    executions = EventExecution.query.filter_by(event_id=event_id).order_by(EventExecution.execution_date.desc()).all()
    
    result = []
    for execution in executions:
        result.append({
            'id': execution.id,
            'date': execution.execution_date.strftime('%Y-%m-%d'),
            'completed': execution.completed,
            'rpe': execution.rpe,
            'notes': execution.notes
        })
        
    return jsonify(result)

@routines_bp.route('/api/event-executions/<int:execution_id>', methods=['PUT'])
@jwt_required()
def update_event_execution(execution_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    # Find execution and verify it belongs to the current user
    execution = EventExecution.query.join(CalendarEvent).filter(
        EventExecution.id == execution_id,
        CalendarEvent.user_id == current_user_id
    ).first()
    
    if not execution:
        return jsonify({"message": "Execution not found"}), 404
        
    try:
        if 'completed' in data:
            execution.completed = data.get('completed')
        if 'rpe' in data:
            execution.rpe = data.get('rpe')
        if 'notes' in data:
            execution.notes = data.get('notes')
            
        db.session.commit()
        
        result = {
            'id': execution.id,
            'date': execution.execution_date.strftime('%Y-%m-%d'),
            'completed': execution.completed,
            'rpe': execution.rpe,
            'notes': execution.notes
        }
        
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/<int:event_id>/toggle-active', methods=['PUT'])
@jwt_required()
def toggle_event_active(event_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if 'active' not in data:
        return jsonify({"message": "Active state is required"}), 400
    
    event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user_id).first()
    if not event:
        return jsonify({"message": "Event not found"}), 404
    
    try:
        event.active = data.get('active')
        db.session.commit()
        
        return jsonify({
            'id': event.id,
            'summary': event.summary,
            'active': event.active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@routines_bp.route('/api/routines/today', methods=['GET'])
@jwt_required()
def get_today_routines():
    current_user_id = get_current_user_id()
    today = date.today()
    
    # Get all commitments for today that are from routines
    commitments = Commitment.query.filter(
        Commitment.user_id == current_user_id,
        Commitment.due_date == today,
        Commitment.routine_id.isnot(None)
    ).all()
    
    result = []
    for commitment in commitments:
        routine = commitment.routine
        session = commitment.session
        
        result.append({
            'id': commitment.id,
            'summary': routine.title,
            'description': routine.description,
            'start_time': session.start_time.strftime('%H:%M') if session.start_time else None,
            'end_time': session.end_time.strftime('%H:%M') if session.end_time else None,
            'rrule': routine.rrule,
            'completed': commitment.completed
        })
    
    return jsonify(result)

@routines_bp.route('/routines/<int:routine_id>/toggle-active', methods=['PUT'])
@jwt_required()
def toggle_routine_active(routine_id):
    """Toggle a routine's active status"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    routine = Routine.query.filter_by(id=routine_id, user_id=user_id).first_or_404()
    
    try:
        routine.active = data.get('active', not routine.active)
        db.session.commit()
        
        # If routine is being activated, create a commitment for today's session
        if routine.active:
            today = date.today()
            session = Session.query.filter(
                Session.routine_id == routine.id,
                Session.start_time >= datetime.combine(today, datetime.min.time()),
                Session.start_time < datetime.combine(today, datetime.max.time())
            ).first()
            
            if session:
                create_commitment_from_routine(routine, session, user_id)
        
        return jsonify(routine.as_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500 