from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, CatchListEntry
from ..utils.helpers import get_current_user_id
from datetime import datetime

catchlist_bp = Blueprint('catchlist', __name__)

@catchlist_bp.route('/api/catchlist', methods=['GET'])
@jwt_required()
def get_catchlist():
    current_user_id = get_current_user_id()
    
    # Check if we should include completed items
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    
    # Base query
    query = CatchListEntry.query.filter_by(user_id=current_user_id)
    
    # Filter out completed items unless explicitly requested
    if not show_completed:
        query = query.filter_by(completed=False)
    
    catchlist_items = query.all()
    
    return jsonify([{
        'id': item.id,
        'content': item.content,
        'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
        'status': item.status,
        'on_daily_todo': item.on_daily_todo,
        'completed': item.completed,
        'completed_at': item.completed_at.strftime('%Y-%m-%d %H:%M') if item.completed_at else None
    } for item in catchlist_items])

@catchlist_bp.route('/api/catchlist', methods=['POST'])
@jwt_required()
def create_catchlist_item():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({"message": "Content is required"}), 400
    
    try:
        new_item = CatchListEntry(
            content=data.get('content'),
            user_id=current_user_id,
            status='active',
            on_daily_todo=data.get('on_daily_todo', False)
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({
            'id': new_item.id,
            'content': new_item.content,
            'created_at': new_item.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': new_item.status,
            'on_daily_todo': new_item.on_daily_todo,
            'completed': new_item.completed,
            'completed_at': None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_bp.route('/api/catchlist/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_catchlist_item(item_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    item = CatchListEntry.query.filter_by(id=item_id, user_id=current_user_id).first()
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    try:
        if 'content' in data:
            item.content = data.get('content')
        if 'status' in data:
            item.status = data.get('status')
        if 'on_daily_todo' in data:
            item.on_daily_todo = data.get('on_daily_todo')
        if 'completed' in data:
            item.completed = data.get('completed')
            if data.get('completed'):
                item.completed_at = datetime.utcnow()
            else:
                item.completed_at = None
        
        db.session.commit()
        return jsonify({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': item.status,
            'on_daily_todo': item.on_daily_todo,
            'completed': item.completed,
            'completed_at': item.completed_at.strftime('%Y-%m-%d %H:%M') if item.completed_at else None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_bp.route('/api/catchlist/<int:item_id>/toggle-today', methods=['POST'])
@jwt_required()
def toggle_on_daily_todo(item_id):
    current_user_id = get_current_user_id()
    item = CatchListEntry.query.filter_by(id=item_id, user_id=current_user_id).first()
    
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    try:
        # Toggle the on_daily_todo status
        item.on_daily_todo = not item.on_daily_todo
        
        db.session.commit()
        return jsonify({
            'id': item.id,
            'on_daily_todo': item.on_daily_todo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_bp.route('/api/catchlist/<int:item_id>/mark-done', methods=['POST'])
@jwt_required()
def mark_item_done(item_id):
    current_user_id = get_current_user_id()
    item = CatchListEntry.query.filter_by(id=item_id, user_id=current_user_id).first()
    
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    try:
        # Mark the item as done
        item.completed = True
        item.completed_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({
            'id': item.id,
            'content': item.content,
            'completed': item.completed,
            'completed_at': item.completed_at.strftime('%Y-%m-%d %H:%M'),
            'points': 10  # Checking off a catchlist item is worth 10 points
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_bp.route('/api/catchlist/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_catchlist_item(item_id):
    current_user_id = get_current_user_id()
    item = CatchListEntry.query.filter_by(id=item_id, user_id=current_user_id).first()
    
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500 