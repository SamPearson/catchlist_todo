from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, CatchListEntry
from ..utils.helpers import get_current_user_id

catchlist_bp = Blueprint('catchlist', __name__)

@catchlist_bp.route('/api/catchlist', methods=['GET'])
@jwt_required()
def get_catchlist():
    current_user_id = get_current_user_id()
    catchlist_items = CatchListEntry.query.filter_by(user_id=current_user_id).all()
    return jsonify([{
        'id': item.id,
        'content': item.content,
        'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
        'status': item.status
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
            status='active'
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({
            'id': new_item.id,
            'content': new_item.content,
            'created_at': new_item.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': new_item.status
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
        
        db.session.commit()
        return jsonify({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': item.status
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