from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.tags.tag_service import TagService, TagValidationError
from src.database.db import db


def _get_target_entity(session, user_id, target_type, target_id):
    """Helper to resolve polymorphic targets for tags
    
    Returns:
        tuple: (entity, error_dict) where error_dict is None if successful,
               or contains error details if target_type is invalid
    """
    valid_types = {"task", "project", "calendar", "routine", "session", "report"}
    
    if target_type not in valid_types:
        return None, {
            "error": f"Invalid target type '{target_type}'. Valid types are: {', '.join(sorted(valid_types))}",
            "code": "INVALID_TARGET_TYPE"
        }
    
    if target_type == "task":
        from src.database.tasks.task_models import Task
        entity = session.query(Task).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "project":
        from src.database.projects.project_models import Project
        entity = session.query(Project).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "calendar":
        from src.database.calendars.calendar_models import Calendar
        entity = session.query(Calendar).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "routine":
        from src.database.routines.routine_models import Routine
        entity = session.query(Routine).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "session":
        from src.database.sessions.session_models import RoutineSession
        entity = session.query(RoutineSession).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "report":
        from src.database.reports.report_models import Report
        entity = session.query(Report).filter_by(id=target_id, user_id=user_id).first()
    
    return entity, None

@jwt_required()
def get_tag(tag_id):
    """Get a specific tag"""
    user_id = get_jwt_identity()
    tag_service = TagService(db.session)
    tag = tag_service.get_tag(tag_id=tag_id, user_id=user_id)
    return jsonify(tag.as_dict()) if tag else ('', 404)


@jwt_required()
def list_tags():
    """List all tags for the current user"""
    user_id = get_jwt_identity()
    tag_service = TagService(db.session)
    tags = tag_service.get_all_by_user(user_id=user_id)
    return jsonify([tag.as_dict() for tag in tags])


@jwt_required()
def create_tag():
    """Create a new tag"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    input_color = data.get('color')
    if input_color:
        if input_color.startswith('#'):
            input_color = input_color[1:]
        if len(input_color) != 6:
            return jsonify({'error': 'Invalid color format. Use #RRGGBB'}), 400
        color = input_color
    else:
        color = '6c757d'

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if len(name) > 50:
        return jsonify({'error': 'Name cannot exceed 50 characters'}), 400


    tag_service = TagService(db.session)
    try:
        tag = tag_service.create_tag(
            name=data.get('name'),
            user_id=user_id,
            color=color
        )
        return jsonify(tag.as_dict()), 201
    except TagValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def update_tag(tag_id):
    """Update a tag"""
    user_id = get_jwt_identity()
    tag_service = TagService(db.session)

    input_data = request.get_json() or {}
    if not input_data:
        return jsonify({'error': 'No update data provided'}), 400

    tag = tag_service.get_tag(tag_id=tag_id, user_id=user_id)
    if not tag:
        return ('', 404)


    try:
        updated_tag = tag_service.update_tag(
            tag_id=tag_id,
            user_id=user_id,
            name=input_data.get('name'),
            color=input_data.get('color')
        )
        return jsonify(updated_tag.as_dict()) if updated_tag else ('', 404)
    except TagValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def delete_tag(tag_id):
    """Delete a tag"""
    user_id = get_jwt_identity()
    tag_service = TagService(db.session)
    if tag_service.delete_tag(tag_id=tag_id, user_id=user_id):
        return ('', 204)
    return ('', 404)


@jwt_required()
def attach_tag():
    """POST /api/tags/attach"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    tag_id = data.get('tag_id')
    t_type = data.get('target_type')
    t_id = data.get('target_id')

    if not all([tag_id, t_type, t_id]):
        return jsonify({"error": "tag_id, target_type, and target_id required"}), 400

    service = TagService(db.session)
    target_tag = service.get_tag(tag_id, user_id)
    if not target_tag:
        return jsonify({"error": f"Tag with id {tag_id} not found"}), 404

    entity, error = _get_target_entity(db.session, user_id, t_type, t_id)
    
    if error:
        return jsonify(error), 422
    
    if not entity:
        return jsonify({"error": f"Target {t_type} with id {t_id} not found"}), 404

    try:
        if service.add_tag_to_entity(tag_id, user_id, entity):
            return jsonify({"success": True}), 200
    except TagValidationError as e:
        return jsonify({"error": e.message}), 400
    return jsonify({"error": "Failed to attach tag"}), 400


@jwt_required()
def detach_tag():
    """POST /api/tags/detach"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    tag_id = data.get('tag_id')
    t_type = data.get('target_type')
    t_id = data.get('target_id')

    if not all([tag_id, t_type, t_id]):
        return jsonify({"error": "tag_id, target_type, and target_id required"}), 400

    service = TagService(db.session)
    target_tag = service.get_tag(tag_id, user_id)
    if not target_tag:
        return jsonify({"error": f"Tag with id {tag_id} not found"}), 404


    entity, error = _get_target_entity(db.session, user_id, t_type, t_id)
    
    if error:
        return jsonify(error), 422
    
    if not entity:
        return jsonify({"error": f"Target {t_type} with id {t_id} not found"}), 404

    try:
        if service.remove_tag_from_entity(tag_id, user_id, entity):
            return jsonify({"success": True}), 200
    except TagValidationError as e:
        return jsonify({"error": e.message}), 400
    return jsonify({"error": "Failed to detach tag"}), 400