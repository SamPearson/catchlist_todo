from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, Comment, ProjectSubtask, CatchListEntry, EventExecution, Project, CalendarEvent
from ..utils.helpers import get_current_user_id

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/api/comments', methods=['POST'])
@jwt_required()
def create_comment():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('content') or not data.get('entity_type') or data.get('entity_id') is None:
        return jsonify({"message": "Missing required fields"}), 400
    
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    
    # Validate that the entity exists and belongs to the current user
    if entity_type == 'project_subtask':
        entity = ProjectSubtask.query.join(Project).filter(
            ProjectSubtask.id == entity_id,
            Project.user_id == current_user_id
        ).first()
    elif entity_type == 'catchlist_entry':
        entity = CatchListEntry.query.filter_by(
            id=entity_id,
            user_id=current_user_id
        ).first()
    elif entity_type == 'event_execution':
        entity = EventExecution.query.join(CalendarEvent).filter(
            EventExecution.id == entity_id,
            CalendarEvent.user_id == current_user_id
        ).first()
    else:
        return jsonify({"message": "Invalid entity type"}), 400
    
    if not entity:
        return jsonify({"message": f"{entity_type.replace('_', ' ').title()} not found"}), 404
    
    try:
        new_comment = Comment(
            content=data.get('content'),
            rpe=data.get('rpe'),
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=current_user_id
        )
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify(new_comment.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@comments_bp.route('/api/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    comment = Comment.query.filter_by(id=comment_id, user_id=current_user_id).first()
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    
    try:
        if 'content' in data:
            comment.content = data.get('content')
        if 'rpe' in data:
            comment.rpe = data.get('rpe')
        
        db.session.commit()
        return jsonify(comment.as_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@comments_bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_current_user_id()
    comment = Comment.query.filter_by(id=comment_id, user_id=current_user_id).first()
    
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@comments_bp.route('/api/comments/<string:entity_type>/<int:entity_id>', methods=['GET'])
@jwt_required()
def get_entity_comments(entity_type, entity_id):
    current_user_id = get_current_user_id()
    
    # Validate the entity exists and belongs to the current user
    if entity_type == 'project_subtask':
        entity = ProjectSubtask.query.join(Project).filter(
            ProjectSubtask.id == entity_id,
            Project.user_id == current_user_id
        ).first()
    elif entity_type == 'catchlist_entry':
        entity = CatchListEntry.query.filter_by(
            id=entity_id,
            user_id=current_user_id
        ).first()
    elif entity_type == 'event_execution':
        entity = EventExecution.query.join(CalendarEvent).filter(
            EventExecution.id == entity_id,
            CalendarEvent.user_id == current_user_id
        ).first()
    else:
        return jsonify({"message": "Invalid entity type"}), 400
    
    if not entity:
        return jsonify({"message": f"{entity_type.replace('_', ' ').title()} not found"}), 404
    
    comments = Comment.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=current_user_id
    ).order_by(Comment.created_at.desc()).all()
    
    return jsonify([comment.as_dict() for comment in comments]) 