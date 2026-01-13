from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.principles.service import PrincipleService, PrincipleValidationError


def _get_target_entity(session, user_id, target_type, target_id):
    """Helper to resolve polymorphic targets for principles"""
    if target_type == "task":
        from src.database.tasks.models import Task
        return session.query(Task).filter_by(id=target_id, user_id=user_id).first()
    if target_type == "project":
        from src.database.projects.models import Project
        return session.query(Project).filter_by(id=target_id, user_id=user_id).first()
    if target_type == "calendar":
        from src.database.calendars.models import Calendar
        return session.query(Calendar).filter_by(id=target_id, user_id=user_id).first()
    if target_type == "routine":
        from src.database.routines.models import Routine
        return session.query(Routine).filter_by(id=target_id, user_id=user_id).first()
    if target_type == "session":
        from src.database.sessions.models import RoutineSession
        return session.query(RoutineSession).filter_by(id=target_id, user_id=user_id).first()
    return None

@jwt_required()
def list_principles():
    """List all principles for the current user"""
    user_id = int(get_jwt_identity())
    service = PrincipleService(db.session)
    items = service.list_principles(user_id)
    return jsonify([p.as_dict() for p in items])

@jwt_required()
def get_principle(principle_id: int):
    """Get a specific principle by ID"""
    user_id = int(get_jwt_identity())
    service = PrincipleService(db.session)
    item = service.get_principle(principle_id, user_id)
    return jsonify(item.as_dict()) if item else ('', 404)

@jwt_required()
def create_principle():
    """Create a new principle"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = PrincipleService(db.session)
    try:
        item = service.create_principle(user_id, data)
        return jsonify(item.as_dict()), 201
    except PrincipleValidationError as e:
        return jsonify({"error": e.message}), 400

@jwt_required()
def update_principle(principle_id: int):
    """Update an existing principle"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = PrincipleService(db.session)
    try:
        updated = service.update_principle(principle_id, user_id, data)
        return jsonify(updated.as_dict()) if updated else ('', 404)
    except PrincipleValidationError as e:
        return jsonify({"error": e.message}), 400

@jwt_required()
def delete_principle(principle_id: int):
    """Delete a principle"""
    user_id = int(get_jwt_identity())
    service = PrincipleService(db.session)
    return ('', 204) if service.delete_principle(principle_id, user_id) else ('', 404)


@jwt_required()
def attach_principle():
    """POST /api/principles/attach"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    p_id = data.get('principle_id')
    t_type = data.get('target_type')
    t_id = data.get('target_id')

    if not all([p_id, t_type, t_id]):
        return jsonify({"error": "principle_id, target_type, and target_id required"}), 400

    service = PrincipleService(db.session)
    entity = _get_target_entity(db.session, user_id, t_type, t_id)
    if not entity:
        return jsonify({"error": f"Target {t_type} with id {t_id} not found"}), 404

    if service.attach_to_entity(p_id, user_id, entity):
        return jsonify({"success": True}), 200
    return jsonify({"error": "Failed to attach principle"}), 400


@jwt_required()
def detach_principle():
    """POST /api/principles/detach"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    p_id = data.get('principle_id')
    t_type = data.get('target_type')
    t_id = data.get('target_id')

    if not all([p_id, t_type, t_id]):
        return jsonify({"error": "principle_id, target_type, and target_id required"}), 400

    service = PrincipleService(db.session)
    entity = _get_target_entity(db.session, user_id, t_type, t_id)
    if not entity:
        return jsonify({"error": f"Target {t_type} with id {t_id} not found"}), 404

    if service.detach_from_entity(p_id, user_id, entity):
        return jsonify({"success": True}), 200
    return jsonify({"error": "Failed to detach principle"}), 400