"""Routes for managing user tags."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.config.models import db, Tag, RoutineTag, SessionTag, ProjectTag, ProjectTaskTag, CatchlistItemTag
from src.config.models import Routine, Session, Project, ProjectTask, CatchlistItem

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('', methods=['GET'])
@jwt_required()
def get_tags():
    """Get all tags for the current user."""
    user_id = get_jwt_identity()
    tags = Tag.query.filter_by(user_id=user_id).all()
    return jsonify({
        'tags': [tag.as_dict() for tag in tags]
    }), 200

@tags_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    """Create a new tag."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'message': 'Tag name is required'}), 400
    
    tag = Tag(
        name=data['name'],
        color=data.get('color', '#6c757d'),
        user_id=user_id
    )
    
    db.session.add(tag)
    db.session.commit()
    
    return jsonify({
        'message': 'Tag created successfully',
        'tag': tag.as_dict()
    }), 201

@tags_bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """Update a tag."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
    if not tag:
        return jsonify({'message': 'Tag not found'}), 404
    
    if 'name' in data:
        tag.name = data['name']
    if 'color' in data:
        tag.color = data['color']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Tag updated successfully',
        'tag': tag.as_dict()
    }), 200

@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """Delete a tag."""
    user_id = get_jwt_identity()
    
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
    if not tag:
        return jsonify({'message': 'Tag not found'}), 404
    
    db.session.delete(tag)
    db.session.commit()
    
    return jsonify({
        'message': 'Tag deleted successfully'
    }), 200

# Routes for tagging items

@tags_bp.route('/apply/<string:entity_type>/<int:entity_id>/<int:tag_id>', methods=['POST'])
@jwt_required()
def apply_tag(entity_type, entity_id, tag_id):
    """Apply a tag to an entity."""
    user_id = get_jwt_identity()
    
    # Verify the tag exists and belongs to the user
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
    if not tag:
        return jsonify({'message': 'Tag not found'}), 404
    
    # Handle different entity types
    if entity_type == 'routine':
        entity = Routine.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Routine not found'}), 404
        
        # Check if tag already applied
        existing = RoutineTag.query.filter_by(routine_id=entity_id, tag_id=tag_id).first()
        if existing:
            return jsonify({'message': 'Tag already applied'}), 400
        
        tag_association = RoutineTag(routine_id=entity_id, tag_id=tag_id)
    
    elif entity_type == 'session':
        entity = Session.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Session not found'}), 404
        
        existing = SessionTag.query.filter_by(session_id=entity_id, tag_id=tag_id).first()
        if existing:
            return jsonify({'message': 'Tag already applied'}), 400
        
        tag_association = SessionTag(session_id=entity_id, tag_id=tag_id)
    
    elif entity_type == 'project':
        entity = Project.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Project not found'}), 404
        
        existing = ProjectTag.query.filter_by(project_id=entity_id, tag_id=tag_id).first()
        if existing:
            return jsonify({'message': 'Tag already applied'}), 400
        
        tag_association = ProjectTag(project_id=entity_id, tag_id=tag_id)
    
    elif entity_type == 'project_task':
        # For project tasks, we need to check if the task's project belongs to the user
        task = ProjectTask.query.filter_by(id=entity_id).first()
        if not task:
            return jsonify({'message': 'Project task not found'}), 404
        
        project = Project.query.filter_by(id=task.project_id, user_id=user_id).first()
        if not project:
            return jsonify({'message': 'Project not found or unauthorized'}), 404
        
        existing = ProjectTaskTag.query.filter_by(project_task_id=entity_id, tag_id=tag_id).first()
        if existing:
            return jsonify({'message': 'Tag already applied'}), 400
        
        tag_association = ProjectTaskTag(project_task_id=entity_id, tag_id=tag_id)
    
    elif entity_type == 'catchlist_item':
        entity = CatchlistItem.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Catchlist item not found'}), 404
        
        existing = CatchlistItemTag.query.filter_by(catchlist_item_id=entity_id, tag_id=tag_id).first()
        if existing:
            return jsonify({'message': 'Tag already applied'}), 400
        
        tag_association = CatchlistItemTag(catchlist_item_id=entity_id, tag_id=tag_id)
    
    else:
        return jsonify({'message': 'Invalid entity type'}), 400
    
    db.session.add(tag_association)
    db.session.commit()
    
    return jsonify({
        'message': 'Tag applied successfully'
    }), 201

@tags_bp.route('/remove/<string:entity_type>/<int:entity_id>/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag(entity_type, entity_id, tag_id):
    """Remove a tag from an entity."""
    user_id = get_jwt_identity()
    
    # Verify the tag exists and belongs to the user
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
    if not tag:
        return jsonify({'message': 'Tag not found'}), 404
    
    # Handle different entity types
    if entity_type == 'routine':
        entity = Routine.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Routine not found'}), 404
        
        association = RoutineTag.query.filter_by(routine_id=entity_id, tag_id=tag_id).first()
    
    elif entity_type == 'session':
        entity = Session.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Session not found'}), 404
        
        association = SessionTag.query.filter_by(session_id=entity_id, tag_id=tag_id).first()
    
    elif entity_type == 'project':
        entity = Project.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Project not found'}), 404
        
        association = ProjectTag.query.filter_by(project_id=entity_id, tag_id=tag_id).first()
    
    elif entity_type == 'project_task':
        # For project tasks, we need to check if the task's project belongs to the user
        task = ProjectTask.query.filter_by(id=entity_id).first()
        if not task:
            return jsonify({'message': 'Project task not found'}), 404
        
        project = Project.query.filter_by(id=task.project_id, user_id=user_id).first()
        if not project:
            return jsonify({'message': 'Project not found or unauthorized'}), 404
        
        association = ProjectTaskTag.query.filter_by(project_task_id=entity_id, tag_id=tag_id).first()
    
    elif entity_type == 'catchlist_item':
        entity = CatchlistItem.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Catchlist item not found'}), 404
        
        association = CatchlistItemTag.query.filter_by(catchlist_item_id=entity_id, tag_id=tag_id).first()
    
    else:
        return jsonify({'message': 'Invalid entity type'}), 400
    
    # If the association doesn't exist, return success since the end goal (tag not being associated) is achieved
    if not association:
        return jsonify({
            'message': 'Tag is not associated with this entity'
        }), 200
    
    db.session.delete(association)
    db.session.commit()
    
    return jsonify({
        'message': 'Tag removed successfully'
    }), 200

@tags_bp.route('/entity/<string:entity_type>/<int:entity_id>', methods=['GET'])
@jwt_required()
def get_entity_tags(entity_type, entity_id):
    """Get all tags for a specific entity."""
    user_id = get_jwt_identity()
    
    # Handle different entity types
    if entity_type == 'routine':
        entity = Routine.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Routine not found'}), 404
        
        tag_ids = [assoc.tag_id for assoc in entity.tag_associations]
    
    elif entity_type == 'session':
        entity = Session.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Session not found'}), 404
        
        tag_ids = [assoc.tag_id for assoc in entity.tag_associations]
    
    elif entity_type == 'project':
        entity = Project.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Project not found'}), 404
        
        tag_ids = [assoc.tag_id for assoc in entity.tag_associations]
    
    elif entity_type == 'project_task':
        # For project tasks, we need to check if the task's project belongs to the user
        task = ProjectTask.query.filter_by(id=entity_id).first()
        if not task:
            return jsonify({'message': 'Project task not found'}), 404
        
        project = Project.query.filter_by(id=task.project_id, user_id=user_id).first()
        if not project:
            return jsonify({'message': 'Project not found or unauthorized'}), 404
        
        tag_ids = [assoc.tag_id for assoc in task.tag_associations]
    
    elif entity_type == 'catchlist_item':
        entity = CatchlistItem.query.filter_by(id=entity_id, user_id=user_id).first()
        if not entity:
            return jsonify({'message': 'Catchlist item not found'}), 404
        
        tag_ids = [assoc.tag_id for assoc in entity.tag_associations]
    
    else:
        return jsonify({'message': 'Invalid entity type'}), 400
    
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    
    return jsonify({
        'tags': [tag.as_dict() for tag in tags]
    }), 200 