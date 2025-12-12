from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.tags.service import TagService
from src.database.db import db


# Create a single instance of the service
tag_service = TagService(db.session)

@jwt_required()
def get_tag(tag_id):
    """Get a specific tag"""
    user_id = get_jwt_identity()
    tag = tag_service.repository.get_by_id(tag_id=tag_id, user_id=user_id)
    return jsonify({'tag': tag.as_dict()}) if tag else ('', 404)

@jwt_required()
def list_tags():
    """List all tags for the current user"""
    user_id = get_jwt_identity()
    tags = tag_service.get_all_by_user(user_id=user_id)
    tag_list = jsonify({
        'tags': [tag.as_dict() for tag in tags]
    })

    return tag_list



@jwt_required()
def create_tag():
    """Create a new tag"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400

    tag = tag_service.create_tag(
        name=data['name'],
        user_id=user_id,
        color=data.get('color', '#6c757d')  # Use default color if not provided
    )
    return jsonify(tag.as_dict()), 201

@jwt_required()
def update_tag(tag_id):
    """Update a tag"""
    user_id = get_jwt_identity()
    tag = tag_service.repository.get_by_id(tag_id=tag_id, user_id=user_id)
    if not tag:
        return ('', 404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    updated_tag = tag_service.update_tag(
        tag_id=tag_id,
        user_id=user_id,
        name=data.get('name'),
        color=data.get('color')
    )
    return jsonify(updated_tag.as_dict()) if updated_tag else ('', 404)

@jwt_required()
def delete_tag(tag_id):
    """Delete a tag"""
    user_id = get_jwt_identity()
    if tag_service.delete_tag(tag_id=tag_id, user_id=user_id):
        return ('', 204)
    return ('', 404)