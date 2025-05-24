from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.models import db, Routine, Session, Commitment
from ..utils.helpers import get_current_user_id
from ...config.caldav_client import CalDAVClient
from datetime import datetime

calendar_events_bp = Blueprint('calendar_events', __name__)

@calendar_events_bp.route('/api/calendar-events', methods=['GET'])
@jwt_required()
def get_calendar_events():
    current_user_id = get_current_user_id()
    routines = Routine.query.filter_by(user_id=current_user_id).all()
    
    result = []
    for routine in routines:
        result.append({
            'id': routine.id,
            'uid': routine.external_uid,
            'title': routine.title,
            'description': routine.description,
            'rrule': routine.rrule,
            'active': routine.active,
            'external_source': routine.external_source
        })
    
    return jsonify(result)

@calendar_events_bp.route('/api/calendar-events', methods=['POST'])
@jwt_required()
def create_calendar_event():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({"message": "Title is required"}), 400
    
    try:
        new_routine = Routine(
            external_uid=data.get('uid', f"manual-{datetime.now().timestamp()}"),
            title=data.get('title'),
            description=data.get('description', ''),
            rrule=data.get('rrule', ''),
            active=True,
            user_id=current_user_id,
            external_source='manual'
        )
        
        db.session.add(new_routine)
        db.session.commit()
        
        result = {
            'id': new_routine.id,
            'uid': new_routine.external_uid,
            'title': new_routine.title,
            'description': new_routine.description,
            'rrule': new_routine.rrule,
            'active': new_routine.active,
            'external_source': new_routine.external_source
        }
        
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@calendar_events_bp.route('/api/calendar-events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_calendar_event(event_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    routine = Routine.query.filter_by(id=event_id, user_id=current_user_id).first()
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
    
    try:
        if 'title' in data:
            routine.title = data.get('title')
        if 'description' in data:
            routine.description = data.get('description')
        if 'rrule' in data:
            routine.rrule = data.get('rrule')
        
        db.session.commit()
        
        result = {
            'id': routine.id,
            'uid': routine.external_uid,
            'title': routine.title,
            'description': routine.description,
            'rrule': routine.rrule,
            'active': routine.active,
            'external_source': routine.external_source
        }
        
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@calendar_events_bp.route('/api/calendar-events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_calendar_event(event_id):
    current_user_id = get_current_user_id()
    routine = Routine.query.filter_by(id=event_id, user_id=current_user_id).first()
    
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
    
    try:
        db.session.delete(routine)
        db.session.commit()
        return jsonify({"message": "Routine deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@calendar_events_bp.route('/api/calendar-events/import', methods=['POST'])
@jwt_required()
def import_caldav_events():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('url'):
        return jsonify({"message": "CalDAV URL is required"}), 400
    
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
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
            new_routine = Routine(
                external_uid=event_dict['uid'],
                title=event_dict['summary'],
                description=event_dict.get('description', ''),
                rrule=event_dict.get('rrule', ''),
                active=True,
                user_id=current_user_id,
                external_source='caldav'
            )
            
            db.session.add(new_routine)
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

@calendar_events_bp.route('/api/calendar-events/<int:event_id>/sessions', methods=['GET'])
@jwt_required()
def get_event_sessions(event_id):
    current_user_id = get_current_user_id()
    routine = Routine.query.filter_by(id=event_id, user_id=current_user_id).first()
    
    if not routine:
        return jsonify({"message": "Routine not found"}), 404
        
    sessions = Session.query.filter_by(routine_id=event_id).order_by(Session.start_time.desc()).all()
    
    result = []
    for session in sessions:
        result.append({
            'id': session.id,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat(),
            'completed': session.completed,
            'rpe': session.rpe,
            'notes': session.notes
        })
        
    return jsonify(result)

@calendar_events_bp.route('/api/sessions/<int:session_id>', methods=['PUT'])
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
            'notes': session.notes
        }
        
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@calendar_events_bp.route('/api/calendar-events/<int:event_id>/toggle-active', methods=['PUT'])
@jwt_required()
def toggle_event_active(event_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if 'active' not in data:
        return jsonify({"message": "Active state is required"}), 400
    
    routine = Routine.query.filter_by(id=event_id, user_id=current_user_id).first()
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