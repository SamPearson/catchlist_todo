from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.projects.project_service import ProjectService, ProjectValidationError
from src.database.projects.project_repository import ProjectRepository
from src.database.base.exceptions import EntityNotFoundError
from src.database.tasks.task_service import TaskService, TaskValidationError
from src.database.tasks.task_repository import TaskRepository


@jwt_required()
def list_projects():
    user_id = int(get_jwt_identity())
    include_completed = request.args.get('include_completed', 'false').lower() == 'true'
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    service = ProjectService(ProjectRepository(db.session))

    projects = service.list_projects(user_id=user_id,
                                     include_completed=include_completed,
                                     include_inactive=include_inactive)
    return jsonify([p.as_dict() for p in projects])


@jwt_required()
def get_project(project_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        project = service.get_project(user_id, project_id)
    except EntityNotFoundError:
        return ('', 404)
    return jsonify(project.as_dict())


@jwt_required()
def create_project():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = ProjectService(ProjectRepository(db.session))

    try:
        project = service.create_project(user_id, data)
        return jsonify(project.as_dict()), 201
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def update_project(project_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        service.get_project(user_id, project_id)
    except EntityNotFoundError:
        return ('', 404)

    data = request.get_json() or {}

    # Check for disallowed fields
    disallowed_fields = {'status', 'active', 'completed', 'completed_at'}
    if any(field in data for field in disallowed_fields):
        return jsonify({
            'error': 'Cannot update status, active, or completed via this endpoint. Use dedicated endpoints instead.'
        }), 400

    try:
        updated = service.update_project(user_id, project_id, data)
        return jsonify(updated.as_dict())
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def complete_project(project_id: int):
    """Mark a project as completed"""
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        completed = service.complete_project(user_id, project_id)
        return jsonify(completed.as_dict())
    except EntityNotFoundError:
        return ('', 404)
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def uncomplete_project(project_id: int):
    """Mark a project as not completed"""
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        uncompleted = service.uncomplete_project(user_id, project_id)
        return jsonify(uncompleted.as_dict())
    except EntityNotFoundError:
        return ('', 404)



@jwt_required()
def activate_project(project_id: int):
    """Activate a project (set active=true) - requires win_condition and reason"""
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        activated = service.activate_project(user_id, project_id)
        return jsonify(activated.as_dict())
    except EntityNotFoundError:
        return ('', 404)
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def deactivate_project(project_id: int):
    """Deactivate a project (set active=false)"""
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        deactivated = service.deactivate_project(user_id, project_id)
        return jsonify(deactivated.as_dict())
    except EntityNotFoundError:
        return ('', 404)
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def change_project_status(project_id: int):
    """Change a project's status"""
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        service.get_project(user_id, project_id)
    except EntityNotFoundError:
        return ('', 404)

    data = request.get_json() or {}
    if not data or 'status' not in data:
        return jsonify({'error': 'status is required'}), 400

    try:
        updated = service.change_status(user_id, project_id, data['status'])
        return jsonify(updated.as_dict())
    except ProjectValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def delete_project(project_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        service.delete_project(user_id, project_id)
        return ('', 204)
    except EntityNotFoundError:
        return ('', 404)


# --- Subtask Routes ---

@jwt_required()
def get_project_tasks(project_id: int):
    user_id = int(get_jwt_identity())
    include_completed = request.args.get('include_completed', 'false').lower() == 'true'
    service = ProjectService(ProjectRepository(db.session))

    try:
        service.get_project(user_id, project_id)
    except EntityNotFoundError:
        return ('', 404)

    tasks = service.get_project_tasks(project_id, user_id, include_completed)
    return jsonify([t.as_dict() for t in tasks])


@jwt_required()
def create_project_task(project_id: int):
    """Create a new task as a subtask of this project"""
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    try:
        service.get_project(user_id, project_id)
    except EntityNotFoundError:
        return ('', 404)

    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    try:
        task = service.create_subtask(user_id, project_id, data['title'], data)
        return jsonify(task.as_dict()), 201
    except (ProjectValidationError, TaskValidationError) as e:
        return jsonify({"error": e.message}), 400

