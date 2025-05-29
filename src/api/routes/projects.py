from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.models import db, Project, ProjectTask, Commitment, Checkin
from ..utils.helpers import get_current_user_id
from datetime import datetime, date
from sqlalchemy import and_
from dateutil.parser import parse as parse_date

projects_bp = Blueprint('projects', __name__)

# Add OPTIONS method handler for CORS preflight requests
@projects_bp.route('/projects/tasks/today', methods=['OPTIONS'])
def options_today_tasks():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@projects_bp.route('/projects/tasks/today', methods=['GET'])
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

@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    current_user_id = get_current_user_id()
    projects = Project.query.filter_by(user_id=current_user_id).all()
    
    result = []
    for project in projects:
        subtasks = []
        for subtask in project.tasks:
            # Check if there's a commitment for today
            today = date.today()
            has_commitment = bool(Commitment.query.filter_by(
                project_task_id=subtask.id,
                due_date=today,
                user_id=current_user_id
            ).first())
            
            subtasks.append({
                'id': subtask.id,
                'title': subtask.title,
                'complete': subtask.complete,
                'has_commitment': has_commitment
            })
        
        result.append({
            'id': project.id,
            'title': project.title,
            'win_condition': project.win_condition,
            'reason': project.reason,
            'next_step': project.next_step,
            'subtasks': subtasks
        })
    
    return jsonify(result)

@projects_bp.route('/projects', methods=['POST'])
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

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
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

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
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

@projects_bp.route('/projects/<int:project_id>/subtasks', methods=['POST'])
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
            description=data.get('description'),
            complete=data.get('complete', False),
            project_id=project_id
        )
        db.session.add(new_subtask)
        db.session.commit()
        
        # If due_date is provided, create a commitment
        if data.get('due_date'):
            commitment = Commitment(
                user_id=current_user_id,
                project_task_id=new_subtask.id,
                due_date=datetime.fromisoformat(data['due_date']).date()
            )
            db.session.add(commitment)
            db.session.commit()
        
        result = new_subtask.as_dict()
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/subtasks/<int:subtask_id>', methods=['OPTIONS'])
def options_subtask(subtask_id):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@projects_bp.route('/subtasks/<int:subtask_id>', methods=['PUT'])
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
    
    if 'description' in data:
        subtask.description = data['description']
        changed_fields.append('description')
    
    if 'complete' in data:
        subtask.complete = data['complete']
        if data['complete']:
            subtask.completed_at = datetime.utcnow()
        changed_fields.append('complete')
    
    if 'due_date' in data:
        try:
            # Handle both ISO format and UTC timestamps
            due_date = parse_date(data['due_date']).date()
            
            # Find or create commitment
            commitment = Commitment.query.filter_by(
                project_task_id=subtask.id,
                due_date=due_date,
                user_id=current_user_id
            ).first()
            
            if not commitment:
                commitment = Commitment(
                    user_id=current_user_id,
                    project_task_id=subtask.id,
                    due_date=due_date
                )
                db.session.add(commitment)
                changed_fields.append('due_date')
        except ValueError as e:
            return jsonify({"message": f"Invalid date format: {str(e)}"}), 400
    
    try:
        db.session.commit()
        
        # Check if there's a commitment for today
        today = date.today()
        has_commitment = bool(Commitment.query.filter_by(
            project_task_id=subtask.id,
            due_date=today,
            user_id=current_user_id
        ).first())
        
        return jsonify({
            'id': subtask.id,
            'title': subtask.title,
            'description': subtask.description,
            'complete': subtask.complete,
            'completed_at': subtask.completed_at.isoformat() if subtask.completed_at else None,
            'has_commitment': has_commitment,
            'changed': changed_fields
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/subtasks/<int:subtask_id>', methods=['DELETE'])
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

@projects_bp.route('/projects/subtasks/fix-dates', methods=['POST'])
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

@projects_bp.route('/subtasks/<int:subtask_id>/checkins', methods=['OPTIONS'])
def options_subtask_checkins(subtask_id):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@projects_bp.route('/subtasks/<int:subtask_id>/checkins', methods=['GET'])
@jwt_required()
def get_subtask_checkins(subtask_id):
    current_user_id = get_current_user_id()
    
    # Check if user owns the project that contains this subtask
    subtask = ProjectTask.query.join(Project).filter(
        ProjectTask.id == subtask_id,
        Project.user_id == current_user_id
    ).first()
    
    if not subtask:
        return jsonify({"message": "Subtask not found"}), 404
    
    # Get all checkins for this subtask directly
    checkins = Checkin.query.filter_by(
        entity_type='project_task',
        entity_id=subtask_id,
        user_id=current_user_id
    ).order_by(Checkin.timestamp.desc()).all()
    
    result = [{
        'id': checkin.id,
        'comment': checkin.comment,
        'timestamp': checkin.timestamp.isoformat(),
        'rpe': checkin.rpe,
        'progress': checkin.progress,
        'mood': checkin.mood,
        'energy': checkin.energy,
        'gains': checkin.gains,
        'gratitudes': checkin.gratitudes
    } for checkin in checkins]
    
    return jsonify(result)

@projects_bp.route('/subtasks/<int:subtask_id>/checkins', methods=['POST'])
@jwt_required()
def add_subtask_checkin(subtask_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    # Check if user owns the project that contains this subtask
    subtask = ProjectTask.query.join(Project).filter(
        ProjectTask.id == subtask_id,
        Project.user_id == current_user_id
    ).first()
    
    if not subtask:
        return jsonify({"message": "Subtask not found"}), 404
    
    try:
        # Create the checkin
        checkin = Checkin(
            user_id=current_user_id,
            entity_type='project_task',
            entity_id=subtask_id,
            comment=data.get('comment', ''),
            rpe=data.get('rpe'),
            progress=data.get('progress'),
            mood=data.get('mood'),
            energy=data.get('energy'),
            gains=data.get('gains'),
            gratitudes=data.get('gratitudes')
        )
        db.session.add(checkin)
        
        # If mark_complete is True, mark the subtask as complete
        if data.get('mark_complete'):
            subtask.complete = True
            subtask.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': checkin.id,
            'comment': checkin.comment,
            'timestamp': checkin.timestamp.isoformat(),
            'rpe': checkin.rpe,
            'progress': checkin.progress,
            'mood': checkin.mood,
            'energy': checkin.energy,
            'gains': checkin.gains,
            'gratitudes': checkin.gratitudes
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500 