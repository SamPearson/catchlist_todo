from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.tags.service import TagService, TagValidationError
from src.database.db import db


# Create a single instance of the service
tag_service = TagService(db.session)

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