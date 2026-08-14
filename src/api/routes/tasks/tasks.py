from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.base.exceptions import EntityNotFoundError
from src.database.tasks.task_service import TaskService, TaskValidationError
from src.database.tasks.task_repository import TaskRepository
from src.database.db import db

# Create a single instance of the service
task_service = TaskService(TaskRepository(db.session))


@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    user_id = get_jwt_identity()
    try:
        task = task_service.get_task(user_id, task_id)
        return jsonify(task.as_dict())
    except EntityNotFoundError:
        return ('', 404)


@jwt_required()
def list_tasks():
    """List all tasks for the current user"""
    user_id = get_jwt_identity()
    include_completed = request.args.get('include_completed', '').lower() == 'true'
    tasks = task_service.list_tasks(user_id=user_id, include_completed=include_completed)
    return jsonify([task.as_dict() for task in tasks])


@jwt_required()
def create_task():
    """Create a new task"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    try:
        task = task_service.create_task(
            user_id=user_id,
            title=data['title'],
            data=data
        )
        return jsonify(task.as_dict()), 201
    except TaskValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def update_task(task_id):
    """Update a task (excludes completion, active, and status)"""
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    try:
        updated_task = task_service.update_task(user_id, task_id, data)
        return jsonify(updated_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)
    except TaskValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    user_id = get_jwt_identity()

    try:
        task_service.delete_task(user_id, task_id)
        return '', 204
    except EntityNotFoundError:
        return '', 404


@jwt_required()
def complete_task(task_id):
    """Mark a task as completed. Query param toggle=true toggles completion instead."""
    user_id = get_jwt_identity()

    try:
        toggle = request.args.get('toggle', 'false').lower() == 'true'

        if toggle:
            completed_task = task_service.toggle_task_completion(user_id, task_id)
        else:
            completed_task = task_service.complete_task(user_id, task_id)

        return jsonify(completed_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)


@jwt_required()
def uncomplete_task(task_id):
    """Mark a task as incomplete"""
    user_id = get_jwt_identity()

    try:
        uncompleted_task = task_service.uncomplete_task(user_id, task_id)
        return jsonify(uncompleted_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)


@jwt_required()
def activate_task(task_id):
    """Activate a task (set active=true)"""
    user_id = get_jwt_identity()

    try:
        activated_task = task_service.activate_task(user_id, task_id)
        return jsonify(activated_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)


@jwt_required()
def deactivate_task(task_id):
    """Deactivate a task (set active=false)"""
    user_id = get_jwt_identity()

    try:
        deactivated_task = task_service.deactivate_task(user_id, task_id)
        return jsonify(deactivated_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)


@jwt_required()
def change_task_status(task_id):
    """Change a task's status"""
    user_id = get_jwt_identity()

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'status is required'}), 400

    try:
        updated_task = task_service.change_status(user_id, task_id, data['status'])
        return jsonify(updated_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)
    except TaskValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def attach_to_project(task_id, project_id):
    """Attach a task to a project"""
    user_id = get_jwt_identity()

    try:
        attached_task = task_service.attach_to_project(user_id, task_id, project_id)
        return jsonify(attached_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)


@jwt_required()
def detach_from_project(task_id):
    """Detach a task from its project"""
    user_id = get_jwt_identity()

    try:
        detached_task = task_service.detach_from_project(user_id, task_id)
        return jsonify(detached_task.as_dict())
    except EntityNotFoundError:
        return ('', 404)
