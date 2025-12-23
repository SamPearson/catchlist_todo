from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.tags.service import TagService, TagValidationError
from src.database.db import db


# Create a single instance of the service
tag_service = TagService(db.session)

def _get_target_entity(session, user_id, target_type, target_id):
    """Helper to resolve polymorphic targets for tags"""
    if target_type == "task":
        from src.database.tasks.models import Task
        return session.query(Task).filter_by(id=target_id, user_id=user_id).first()
    if target_type == "project":
        from src.database.projects.models import Project
        return session.query(Project).filter_by(id=target_id, user_id=user_id).first()
    if target_type == "routine":
        from src.database.routines.models import Routine
        return session.query(Routine).filter_by(id=target_id, user_id=user_id).first()
    if target_type == "session":
        from src.database.sessions.models import Session
        return session.query(Session).filter_by(id=target_id, user_id=user_id).first()
    return None

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

    tag_service = TagService(db.session)
    try:
        tag = tag_service.create_tag(
            name=data.get('name'),
            user_id=user_id,
            color=data.get('color', '#6c757d')
        )
        return jsonify(tag.as_dict()), 201
    except TagValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def update_tag(tag_id):
    """Update a tag"""
    user_id = get_jwt_identity()
    tag_service = TagService(db.session)
    
    tag = tag_service.get_tag(tag_id=tag_id, user_id=user_id)
    if not tag:
        return ('', 404)

    data = request.get_json() or {}
    try:
        updated_tag = tag_service.update_tag(
            tag_id=tag_id,
            user_id=user_id,
            name=data.get('name'),
            color=data.get('color')
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
    entity = _get_target_entity(db.session, user_id, t_type, t_id)
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
    entity = _get_target_entity(db.session, user_id, t_type, t_id)
    if not entity:
        return jsonify({"error": f"Target {t_type} with id {t_id} not found"}), 404

    try:
        if service.remove_tag_from_entity(tag_id, user_id, entity):
            return jsonify({"success": True}), 200
    except TagValidationError as e:
        return jsonify({"error": e.message}), 400
    return jsonify({"error": "Failed to detach tag"}), 400