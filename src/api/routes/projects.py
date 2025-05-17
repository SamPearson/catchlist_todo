from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.models import db, Project, ProjectTask, TaskExecution, Commitment
from ..utils.helpers import get_current_user_id
from datetime import datetime, date
from sqlalchemy import and_

projects_bp = Blueprint('projects', __name__)

# Add OPTIONS method handler for CORS preflight requests
@projects_bp.route('/api/projects/tasks/today', methods=['OPTIONS'])
def options_today_tasks():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@projects_bp.route('/api/projects/tasks/today', methods=['GET'])
@jwt_required()
def get_today_tasks():
    """Get all project tasks due today for the current user"""
    current_user_id = get_current_user_id()
    today = date.today()
    
    # Get all tasks with active commitments for today
    tasks = db.session.query(
        ProjectTask,
        Project.title.label('project_title')
    ).join(
        Project, ProjectTask.project_id == Project.id
    ).join(
        Commitment,
        and_(
            Commitment.project_task_id == ProjectTask.id,
            Commitment.due_date == today,
            Commitment.user_id == current_user_id,
            Commitment.completed == False
        )
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

@projects_bp.route('/api/projects', methods=['GET'])
@jwt_required()
def get_projects():
    current_user_id = get_current_user_id()
    projects = Project.query.filter_by(user_id=current_user_id).all()
    
    result = []
    for project in projects:
        subtasks = [{
            'id': subtask.id,
            'title': subtask.title,
            'complete': subtask.complete,
            'on_daily_todo': subtask.on_daily_todo if hasattr(subtask, 'on_daily_todo') else False
        } for subtask in project.tasks]
        
        result.append({
            'id': project.id,
            'title': project.title,
            'win_condition': project.win_condition,
            'reason': project.reason,
            'next_step': project.next_step,
            'subtasks': subtasks
        })
    
    return jsonify(result)

@projects_bp.route('/api/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({"message": "Project title is required"}), 400
    
    try:
        new_project = Project(
            title=data.get('title'),
            win_condition=data.get('win_condition', ''),
            reason=data.get('reason', ''),
            next_step=data.get('next_step', ''),
            user_id=current_user_id
        )
        db.session.add(new_project)
        db.session.commit()
        
        result = {
            'id': new_project.id,
            'title': new_project.title,
            'win_condition': new_project.win_condition,
            'reason': new_project.reason,
            'next_step': new_project.next_step,
            'subtasks': []
        }
        
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({"message": "Project not found"}), 404
    
    try:
        project.title = data.get('title', project.title)
        project.win_condition = data.get('win_condition', project.win_condition)
        project.reason = data.get('reason', project.reason)
        project.next_step = data.get('next_step', project.next_step)
        
        db.session.commit()
        
        result = {
            'id': project.id,
            'title': project.title,
            'win_condition': project.win_condition,
            'reason': project.reason,
            'next_step': project.next_step
        }
        
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    current_user_id = get_current_user_id()
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    
    if not project:
        return jsonify({"message": "Project not found"}), 404
    
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>/subtasks', methods=['POST'])
@jwt_required()
def create_subtask(project_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({"message": "Subtask title is required"}), 400
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({"message": "Project not found"}), 404
    
    try:
        new_subtask = ProjectTask(
            title=data.get('title'),
            complete=data.get('complete', False),
            project_id=project_id
        )
        db.session.add(new_subtask)
        db.session.commit()
        
        result = {
            'id': new_subtask.id,
            'title': new_subtask.title,
            'complete': new_subtask.complete,
            'on_daily_todo': False
        }
        
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/api/subtasks/<int:subtask_id>', methods=['OPTIONS'])
def options_subtask(subtask_id):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@projects_bp.route('/api/subtasks/<int:subtask_id>', methods=['PUT'])
@jwt_required()
def update_subtask(subtask_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    subtask = ProjectTask.query.get(subtask_id)
    if not subtask:
        return jsonify({"message": "Subtask not found"}), 404
    
    # Check if user owns the project that contains this subtask
    project = Project.query.filter_by(id=subtask.project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({"message": "Not authorized"}), 403
    
    changed_fields = []
    
    if 'title' in data:
        subtask.title = data['title']
        changed_fields.append('title')
    
    if 'complete' in data:
        subtask.complete = data['complete']
        changed_fields.append('complete')
    
    if 'on_daily_todo' in data:
        today = date.today()
        
        # Check if there's already a commitment for today
        existing_commitment = Commitment.query.filter_by(
            project_task_id=subtask.id,
            due_date=today,
            user_id=current_user_id
        ).first()
        
        if data['on_daily_todo'] and not existing_commitment:
            # Create new commitment
            commitment = Commitment(
                user_id=current_user_id,
                project_task_id=subtask.id,
                due_date=today
            )
            db.session.add(commitment)
        elif not data['on_daily_todo'] and existing_commitment:
            # Remove from today's list
            db.session.delete(existing_commitment)
    
    try:
        db.session.commit()
        
        # Check if there's a commitment for today after our changes
        on_daily_todo = bool(Commitment.query.filter_by(
            project_task_id=subtask.id,
            due_date=date.today(),
            user_id=current_user_id
        ).first())
        
        return jsonify({
            'id': subtask.id,
            'title': subtask.title,
            'complete': subtask.complete,
            'on_daily_todo': on_daily_todo,
            'changed': changed_fields
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/api/subtasks/<int:subtask_id>', methods=['DELETE'])
@jwt_required()
def delete_subtask(subtask_id):
    current_user_id = get_current_user_id()
    
    subtask = ProjectTask.query.join(Project).filter(
        ProjectTask.id == subtask_id,
        Project.user_id == current_user_id
    ).first()
    
    if not subtask:
        return jsonify({"message": "Subtask not found"}), 404
    
    try:
        db.session.delete(subtask)
        db.session.commit()
        return jsonify({"message": "Subtask deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/api/projects/subtasks/fix-dates', methods=['POST'])
@jwt_required()
def fix_subtask_dates():
    current_user_id = get_current_user_id()
    
    try:
        # Find all completed project subtasks with future dates
        today = datetime.utcnow()
        
        # First get all projects for this user
        projects = Project.query.filter_by(user_id=current_user_id).all()
        project_ids = [p.id for p in projects]
        
        subtasks = ProjectTask.query.filter(
            ProjectTask.project_id.in_(project_ids),
            ProjectTask.complete == True,
            ProjectTask.updated_at > today
        ).all()
        
        updated_count = 0
        for subtask in subtasks:
            subtask.updated_at = today
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully updated {updated_count} project subtasks",
            "updated_count": updated_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500 