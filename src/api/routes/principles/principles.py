from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.db import db
from src.database.principles.service import PrincipleService, PrincipleValidationError

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