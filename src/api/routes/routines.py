from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.models import db, CalendarEvent, EventExecution
from ..utils.helpers import get_current_user_id
from ...config.caldav_client import CalDAVClient
from datetime import datetime

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
    events = CalendarEvent.query.filter_by(user_id=current_user_id).all()
    
    result = []
    for event in events:
        result.append({
            'id': event.id,
            'uid': event.uid,
            'summary': event.summary,
            'description': event.description,
            'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
            'rrule': event.rrule,
            'active': event.active
        })
    
    return jsonify(result)

@routines_bp.route('/api/routines', methods=['POST'])
@jwt_required()
def create_routine():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('summary'):
        return jsonify({"message": "Summary is required"}), 400
    
    try:
        start_time = datetime.strptime(data.get('start_time', '00:00'), '%H:%M')
        end_time = datetime.strptime(data.get('end_time', '00:00'), '%H:%M')
        
        new_event = CalendarEvent(
            uid=data.get('uid', f"manual-{datetime.now().timestamp()}"),
            summary=data.get('summary'),
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            rrule=data.get('rrule', ''),
            user_id=current_user_id
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        result = {
            'id': new_event.id,
            'uid': new_event.uid,
            'summary': new_event.summary,
            'description': new_event.description,
            'start_time': new_event.start_time.strftime('%H:%M'),
            'end_time': new_event.end_time.strftime('%H:%M'),
            'rrule': new_event.rrule
        }
        
        return jsonify(result), 201
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
            
        # Check if event already exists to avoid duplicates
        existing_event = CalendarEvent.query.filter_by(uid=event_dict['uid'], user_id=current_user_id).first()
        if existing_event:
            continue
            
        try:
            # Convert datetime objects to appropriate format
            start_time = event_dict['start']
            end_time = event_dict['end']
            
            new_event = CalendarEvent(
                uid=event_dict['uid'],
                summary=event_dict['summary'],
                description=event_dict.get('description', ''),
                start_time=start_time,
                end_time=end_time,
                rrule=event_dict.get('rrule', ''),
                active=True,
                user_id=current_user_id
            )
            
            db.session.add(new_event)
            imported_count += 1
        except Exception as e:
            print(f"Error importing event: {str(e)}")
            
    try:
        db.session.commit()
        return jsonify({
            "success": True, 
            "message": f"Successfully imported {imported_count} events", 
            "imported_count": imported_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error saving imported events: {str(e)}"}), 500

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
    events = CalendarEvent.query.filter_by(user_id=current_user_id, active=True).all()
    
    today = datetime.today()
    
    result = []
    for event in events:
        # Add logic here to determine if this routine should be shown today
        # For now, just return all active routines
        result.append({
            'id': event.id,
            'uid': event.uid,
            'summary': event.summary,
            'description': event.description,
            'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
            'rrule': event.rrule
        })
    
    return jsonify(result) 