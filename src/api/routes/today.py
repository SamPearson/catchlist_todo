from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from database import Project
from src.database.db import db

from src.config.models.routines import Routine, Session
from src.config.models.commitment import Commitment
from src.config.models.catchlist import CatchlistItem


from ..utils.helpers import get_current_user_id
from datetime import datetime, date

today_bp = Blueprint('today', __name__)

@today_bp.route('/api/today/events', methods=['GET'])
@jwt_required()
def get_today_events():
    current_user_id = get_current_user_id()
    today = date.today()
    
    # Get all sessions for today
    sessions = Session.query.join(Routine).filter(
        Session.user_id == current_user_id,
        db.func.date(Session.start_time) == today,
        Routine.active == True  # Only get sessions from active routines
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
            'is_current': False,  # Will be set below
            'is_all_day': ((session.start_time.strftime('%H:%M') if session.start_time else None) == '00:00' and
                          (session.end_time.strftime('%H:%M') if session.end_time else None) == '00:00')
        })
    
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
    
    # Get today's date in local time
    now = datetime.now()
    today = date(now.year, now.month, now.day)
    
    # Get all tasks that have commitments for today
    tasks = db.session.query(
        ProjectTask, 
        Project.title.label('project_title')
    ).join(
        Project, 
        ProjectTask.project_id == Project.id
    ).join(
        Commitment,
        Commitment.project_task_id == ProjectTask.id
    ).filter(
        Project.user_id == current_user_id,
        Commitment.due_date == today,
        Commitment.completed == False
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

@today_bp.route('/api/today/session-check-in/<int:session_id>', methods=['POST'])
@jwt_required()
def check_in_session(session_id):
    current_user_id = get_current_user_id()
    data = request.get_json() or {}
    
    # Find the session
    session = Session.query.get(session_id)
    if not session:
        return jsonify({"message": "Session not found"}), 404
    
    # Verify user owns this session through the routine
    routine = Routine.query.get(session.routine_id)
    if not routine or routine.user_id != current_user_id:
        return jsonify({"message": "Not authorized"}), 403
    
    # Mark as completed if not already completed
    if not session.completed:
        session.completed = True
    
    # Update RPE and notes if provided
    if 'rpe' in data:
        session.rpe = data.get('rpe')
    
    if 'notes' in data:
        session.notes = data.get('notes')
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Check-in successful",
            "rpe": session.rpe,
            "notes": session.notes
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@today_bp.route('/api/today/tasks/<int:task_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_task_completion(task_id):
    current_user_id = get_current_user_id()
    
    # Find the task
    task = ProjectTask.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404
    
    # Verify user owns this task through the project
    project = Project.query.get(task.project_id)
    if not project or project.user_id != current_user_id:
        return jsonify({"message": "Not authorized"}), 403
    
    # Toggle completion status
    task.complete = not task.complete
    
    # Update the commitment for today
    today_date = date.today()
    commitment = Commitment.query.filter_by(
        project_task_id=task.id,
        due_date=today_date,
        user_id=current_user_id
    ).first()
    
    if commitment:
        commitment.completed = task.complete
        commitment.completed_at = datetime.utcnow() if task.complete else None
    
    try:
        db.session.commit()
        return jsonify({
            "id": task.id,
            "complete": task.complete
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@today_bp.route('/api/today/items', methods=['GET'])
@jwt_required()
def get_today_items():
    current_user_id = get_current_user_id()
    today = date.today()
    
    # Get all items for today
    items = CatchlistItem.query.filter_by(
        user_id=current_user_id,
        completed=False
    ).all()
    
    return jsonify([{
        'id': item.id,
        'content': item.content,
        'type': 'catchlist_item',
        'has_commitment_today': bool(Commitment.query.filter_by(
            catchlist_item_id=item.id,
            due_date=today,
            completed=False
        ).first())
    } for item in items])