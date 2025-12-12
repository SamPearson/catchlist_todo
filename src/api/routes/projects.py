from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from src.database.projects.service import ProjectService
from src.database.projects.repositories import ProjectRepository
from src.database.db import db
from ..utils.helpers import get_current_user_id

projects_bp = Blueprint('projects', __name__)

# Create a single instance of the service
project_service = ProjectService(ProjectRepository(db.session))

@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    current_user_id = get_current_user_id()
    projects = project_service.list_projects(user_id=current_user_id)
    return jsonify([project.as_dict() for project in projects])

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    current_user_id = get_current_user_id()
    project = project_service.get_project(project_id=project_id, user_id=current_user_id)

    if not project:
        return jsonify({"message": "Project not found"}), 404

    return jsonify(project.as_dict())

@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = get_current_user_id()
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"message": "Project title is required"}), 400

    try:
        project = project_service.create_project(
            user_id=current_user_id,
            data=data
        )
        return jsonify(project.as_dict()), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    current_user_id = get_current_user_id()
    project = project_service.get_project(project_id=project_id, user_id=current_user_id)
    
    if not project:
        return jsonify({"message": "Project not found"}), 404

    try:
        data = request.get_json()
        updated_project = project_service.update_project(project, data)
        return jsonify(updated_project.as_dict())
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    current_user_id = get_current_user_id()
    project = project_service.get_project(project_id=project_id, user_id=current_user_id)

    if not project:
        return jsonify({"message": "Project not found"}), 404

    try:
        project_service.delete_project(project)
        return jsonify({"message": "Project deleted successfully"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@projects_bp.route('/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_project_tasks(project_id):
    """Get all tasks associated with a project"""
    current_user_id = get_current_user_id()

    # Get include_completed parameter from query string, default to False
    include_completed = request.args.get('include_completed', 'false').lower() == 'true'

    project = project_service.get_project(project_id, current_user_id)
    if not project:
        return jsonify({"message": "Project not found"}), 404

    tasks = project_service.get_project_tasks(project_id, current_user_id, include_completed)
    return jsonify([task.as_dict() for task in tasks])


@projects_bp.route('/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_subtask(project_id):
    current_user_id = get_current_user_id()
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"message": "Subtask title is required"}), 400

    project = project_service.get_project(project_id=project_id, user_id=current_user_id)
    if not project:
        return jsonify({"message": "Project not found"}), 404

    try:
        task = project_service.create_task(
            project=project,
            user_id=current_user_id,
            data=data
        )
        return jsonify(task.as_dict()), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_subtask(project_id: int, task_id: int):
    current_user_id = get_current_user_id()
    task = project_service.repository.get_task_by_id(task_id, current_user_id)

    if not task:
        return jsonify({"message": "Subtask not found"}), 404

    if task.project_id != project_id:
        return jsonify({"message": "Subtask does not belong to this project"}), 404

    try:
        data = request.get_json()
        updated_task = project_service.update_task(task, data)
        return jsonify(updated_task.as_dict())
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_subtask(project_id: int, task_id: int):
    current_user_id = get_current_user_id()
    task = project_service.repository.get_task_by_id(task_id, current_user_id)

    if not task:
        return jsonify({"message": "Subtask not found"}), 404

    if task.project_id != project_id:
        return jsonify({"message": "Subtask does not belong to this project"}), 404

    try:
        project_service.delete_task(task)
        return jsonify({"message": "Subtask deleted"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500