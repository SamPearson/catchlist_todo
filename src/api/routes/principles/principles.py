from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.base.exceptions import EntityNotFoundError
from src.database.db import db
from src.database.principles.service import PrincipleService, PrincipleValidationError


def _get_target_entity(session, user_id, target_type, target_id):
    """Helper to resolve polymorphic targets for principles
    
    Returns:
        tuple: (entity, error_dict) where error_dict is None if successful,
               or contains error details if target_type is invalid
    """
    valid_types = {"task", "project", "calendar", "routine", "session"}
    
    if target_type not in valid_types:
        return None, {
            "error": f"Invalid target type '{target_type}'. Valid types are: {', '.join(sorted(valid_types))}",
            "code": "INVALID_TARGET_TYPE"
        }
    
    if target_type == "task":
        from src.database.tasks.models import Task
        entity = session.query(Task).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "project":
        from src.database.projects.models import Project
        entity = session.query(Project).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "calendar":
        from src.database.calendars.models import Calendar
        entity = session.query(Calendar).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "routine":
        from src.database.routines.models import Routine
        entity = session.query(Routine).filter_by(id=target_id, user_id=user_id).first()
    elif target_type == "session":
        from src.database.sessions.models import RoutineSession
        entity = session.query(RoutineSession).filter_by(id=target_id, user_id=user_id).first()
    
    return entity, None

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

    input_color = data.get('color')
    if input_color:
        if input_color.startswith('#'):
            input_color = input_color[1:]
        if len(input_color) != 6:
            return jsonify({'error': 'Invalid color format. Use #RRGGBB'}), 400


    service = PrincipleService(db.session)
    try:
        item = service.create_principle(user_id, data)
        return jsonify(item.as_dict()), 201
    except PrincipleValidationError as e:
        return jsonify({"error": str(e)}), 400

@jwt_required()
def update_principle(principle_id: int):
    """Update an existing principle"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if 'color' in data:
        input_color = data.get('color')
        if input_color.startswith('#'):
            input_color = input_color[1:]
        if len(input_color) != 6:
            return jsonify({'error': 'Invalid color format. Use #RRGGBB'}), 400
        data['color'] = input_color

    service = PrincipleService(db.session)
    try:
        updated = service.update_principle(principle_id, user_id, data)
        return jsonify(updated.as_dict()) if updated else ('', 404)
    except EntityNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except PrincipleValidationError as e:
        return jsonify({"error": str(e)}), 400

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
    entity, error = _get_target_entity(db.session, user_id, t_type, t_id)
    
    if error:
        return jsonify(error), 422
    
    if not entity:
        return jsonify({"error": f"Target {t_type} with id {t_id} not found"}), 404

    try:
        if service.attach_to_entity(p_id, user_id, entity):
            return jsonify({"success": True}), 200
    except EntityNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except PrincipleValidationError as e:
        return jsonify({"error": str(e)}), 400

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
    entity, error = _get_target_entity(db.session, user_id, t_type, t_id)
    
    if error:
        return jsonify(error), 422
    
    if not entity:
        return jsonify({"error": f"Target {t_type} with id {t_id} not found"}), 404

    try:
        if service.detach_from_entity(p_id, user_id, entity):
            return jsonify({"success": True}), 200
    except EntityNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except PrincipleValidationError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": "Failed to detach principle"}), 400