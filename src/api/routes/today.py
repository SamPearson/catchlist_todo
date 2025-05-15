from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, CalendarEvent, EventExecution, ProjectSubtask
from ..utils.helpers import get_current_user_id
from datetime import datetime, date

today_bp = Blueprint('today', __name__)

@today_bp.route('/api/today/events', methods=['GET'])
@jwt_required()
def get_today_events():
    current_user_id = get_current_user_id()
    
    # Get all active recurring events
    events = CalendarEvent.query.filter_by(
        user_id=current_user_id,
        active=True
    ).all()
    
    today_date = date.today()
    
    result = []
    for event in events:
        # Check if the event has an execution for today
        execution = EventExecution.query.filter_by(
            event_id=event.id,
            execution_date=today_date
        ).first()
        
        # If execution doesn't exist, create it
        if not execution:
            execution = EventExecution(
                event_id=event.id,
                execution_date=today_date,
                completed=None,
                rpe=None,
                notes=None
            )
            db.session.add(execution)
            
        result.append({
            'id': execution.id,
            'event_id': event.id,
            'summary': event.summary,
            'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
            'description': event.description,
            'completed': execution.completed,
            'rpe': execution.rpe,
            'is_current': False  # This would be calculated based on current time
        })
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
    
    # Sort events by start time
    result.sort(key=lambda x: x['start_time'] if x['start_time'] else '23:59')
    
    # Set current event based on current time
    current_time = datetime.now().strftime('%H:%M')
    for i, event in enumerate(result):
        if i < len(result) - 1:
            current_start = event['start_time'] or '00:00'
            next_start = result[i+1]['start_time'] or '23:59'
            
            if current_start <= current_time < next_start:
                event['is_current'] = True
                break
    
    return jsonify(result)