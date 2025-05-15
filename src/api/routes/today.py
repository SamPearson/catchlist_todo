from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, CalendarEvent, EventExecution, ProjectSubtask, Project, CatchListEntry, TaskExecution
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
                notes=None,
                check_in_count=0
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
            'notes': execution.notes,
            'check_in_count': execution.check_in_count or 0,
            'is_current': False,  # Will be set below
            'is_all_day': ((event.start_time.strftime('%H:%M') if event.start_time else None) == '00:00' and
                           (event.end_time.strftime('%H:%M') if event.end_time else None) == '00:00')
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
    
    # First, set all all-day events as current
    for event in result:
        if event['is_all_day']:
            event['is_current'] = True
    
    # Then, for non-all-day events, use the time-based approach
    non_all_day_events = [e for e in result if not e['is_all_day']]
    for i, event in enumerate(non_all_day_events):
        if i < len(non_all_day_events) - 1:
            current_start = event['start_time'] or '00:00'
            next_start = non_all_day_events[i+1]['start_time'] or '23:59'
            
            if current_start <= current_time < next_start:
                event['is_current'] = True
                break
    
    return jsonify(result)

@today_bp.route('/api/today/tasks', methods=['GET'])
@jwt_required()
def get_today_tasks():
    current_user_id = get_current_user_id()
    
    # Join with Project to get the project title
    tasks = db.session.query(
        ProjectSubtask, 
        Project.title.label('project_title')
    ).join(
        Project, 
        ProjectSubtask.project_id == Project.id
    ).filter(
        Project.user_id == current_user_id,
        ProjectSubtask.on_daily_todo == True
    ).all()
    
    result = []
    for task, project_title in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'complete': task.complete,
            'project_id': task.project_id,
            'project_title': project_title
        })
    
    return jsonify(result)

@today_bp.route('/api/today/event-check-in/<int:execution_id>', methods=['POST'])
@jwt_required()
def check_in_event(execution_id):
    current_user_id = get_current_user_id()
    data = request.get_json() or {}
    
    # Find the execution
    execution = EventExecution.query.get(execution_id)
    if not execution:
        return jsonify({"message": "Execution not found"}), 404
    
    # Verify user owns this execution through the event
    event = CalendarEvent.query.get(execution.event_id)
    if not event or event.user_id != current_user_id:
        return jsonify({"message": "Not authorized"}), 403
    
    # Mark as completed if not already completed
    if not execution.completed:
        execution.completed = "yes"
    
    # Update RPE and notes if provided
    if 'rpe' in data:
        execution.rpe = data.get('rpe')
    
    if 'notes' in data:
        execution.notes = data.get('notes')
    
    # Increment check-in count
    if execution.check_in_count is None:
        execution.check_in_count = 1
    else:
        execution.check_in_count += 1
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Check-in successful",
            "check_in_count": execution.check_in_count,
            "rpe": execution.rpe,
            "notes": execution.notes,
            "points": execution.check_in_count * 10  # 10 points per check-in
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@today_bp.route('/api/today/tasks/<int:task_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_task_completion(task_id):
    current_user_id = get_current_user_id()
    
    # Find the task
    task = ProjectSubtask.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404
    
    # Verify user owns this task through the project
    project = Project.query.get(task.project_id)
    if not project or project.user_id != current_user_id:
        return jsonify({"message": "Not authorized"}), 403
    
    # Toggle completion status
    task.complete = not task.complete
    
    # Update the TaskExecution record for today
    today_date = date.today()
    execution = TaskExecution.query.filter_by(
        task_id=task.id,
        execution_date=today_date
    ).first()
    
    # If no execution record exists yet, create one
    if not execution:
        execution = TaskExecution(
            task_id=task.id,
            project_id=task.project_id,
            user_id=current_user_id,
            execution_date=today_date,
            attempted=True,
            completed=False
        )
        db.session.add(execution)
    
    # Update the execution completion status
    execution.completed = task.complete
    
    try:
        db.session.commit()
        return jsonify({
            "id": task.id,
            "complete": task.complete
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@today_bp.route('/api/today/catchlist', methods=['GET'])
@jwt_required()
def get_today_catchlist():
    current_user_id = get_current_user_id()
    
    # Get all catchlist entries marked for today
    items = CatchListEntry.query.filter_by(
        user_id=current_user_id,
        on_daily_todo=True
    ).all()
    
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': item.status,
            'on_daily_todo': item.on_daily_todo
        })
    
    return jsonify(result)