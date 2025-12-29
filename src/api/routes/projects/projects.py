from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.projects.service import ProjectService, ProjectValidationError
from src.database.projects.repository import ProjectRepository


@jwt_required()
def list_projects():
    user_id = int(get_jwt_identity())
    include_completed = request.args.get('include_completed', 'false').lower() == 'true'
    service = ProjectService(ProjectRepository(db.session))

    projects = service.list_projects(user_id=user_id, include_completed=include_completed)
    return jsonify([p.as_dict() for p in projects])


@jwt_required()
def get_project(project_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    project = service.get_project(project_id, user_id)
    return jsonify(project.as_dict()) if project else ('', 404)


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

    project = service.get_project(project_id, user_id)
    if not project:
        return ('', 404)

    try:
        data = request.get_json() or {}
        updated = service.update_project(project, data)
        return jsonify(updated.as_dict())
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def delete_project(project_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    project = service.get_project(project_id, user_id)
    if not project:
        return ('', 404)

    service.delete_project(project)
    return ('', 204)


# --- Task Sub-routes ---

@jwt_required()
def get_project_tasks(project_id: int):
    user_id = int(get_jwt_identity())
    include_completed = request.args.get('include_completed', 'false').lower() == 'true'
    service = ProjectService(ProjectRepository(db.session))

    project = service.get_project(project_id, user_id)
    if not project:
        return ('', 404)

    tasks = service.get_project_tasks(project_id, user_id, include_completed)
    return jsonify([t.as_dict() for t in tasks])


@jwt_required()
def create_project_task(project_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    project = service.get_project(project_id, user_id)
    if not project:
        return ('', 404)

    try:
        data = request.get_json() or {}
        task = service.create_task(project, user_id, data)
        return jsonify(task.as_dict()), 201
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def update_project_task(project_id: int, task_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    task = service.repository.get_task_by_id(task_id, user_id)
    if not task or task.project_id != project_id:
        return ('', 404)

    try:
        data = request.get_json() or {}
        updated = service.update_task(task, data)
        return jsonify(updated.as_dict())
    except ProjectValidationError as e:
        return jsonify({"error": e.message}), 400


@jwt_required()
def delete_project_task(project_id: int, task_id: int):
    user_id = int(get_jwt_identity())
    service = ProjectService(ProjectRepository(db.session))

    task = service.repository.get_task_by_id(task_id, user_id)
    if not task or task.project_id != project_id:
        return ('', 404)

    service.delete_task(task)
    return ('', 204)