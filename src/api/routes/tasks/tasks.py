from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.tasks.service import TaskService
from src.database.tasks.repositories import TaskRepository
from src.database.db import db

# Create a single instance of the service
task_service = TaskService(TaskRepository(db.session))


@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    return jsonify(task.as_dict()) if task else ('', 404)


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

    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400

    task = task_service.create_task(
        user_id=user_id,
        content=data['content']
    )
    return jsonify(task.as_dict()), 201


@jwt_required()
def update_task(task_id):
    """Update a task"""
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    if not task:
        return ('', 404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    updated_task = task_service.update_task(task, data)
    return jsonify(updated_task.as_dict())


@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    if not task:
        return ('', 404)

    task_service.delete_task(task)
    return ('', 204)

