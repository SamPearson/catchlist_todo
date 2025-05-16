from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.models import db, CatchlistItem, Commitment
from ..utils.helpers import get_current_user_id
from datetime import datetime, date

catchlist_items_bp = Blueprint('catchlist_items', __name__)

@catchlist_items_bp.route('/api/catchlist-items', methods=['GET'])
@jwt_required()
def get_catchlist_items():
    current_user_id = get_current_user_id()
    
    # Check if we should include completed items
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    
    # Base query
    query = CatchlistItem.query.filter_by(user_id=current_user_id)
    
    # Filter out completed items unless explicitly requested
    if not show_completed:
        query = query.filter_by(completed=False)
    
    catchlist_items = query.all()
    
    return jsonify([{
        'id': item.id,
        'content': item.content,
        'created_at': item.created_at.isoformat(),
        'updated_at': item.updated_at.isoformat(),
        'status': item.status,
        'completed': item.completed,
        'completed_at': item.completed_at.isoformat() if item.completed_at else None,
        # Check if there's an active commitment for this item for today
        'on_daily_todo': bool(Commitment.query.filter_by(
            task_id=item.id,
            entity_type='catchlist_item',
            due_date=date.today(),
            completed=False
        ).first())
    } for item in catchlist_items])

@catchlist_items_bp.route('/api/catchlist-items', methods=['POST'])
@jwt_required()
def create_catchlist_item():
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({"message": "Content is required"}), 400
    
    try:
        new_item = CatchlistItem(
            content=data.get('content'),
            user_id=current_user_id,
            status='active'
        )
        db.session.add(new_item)
        db.session.commit()
        
        # Create a commitment for today if requested
        if data.get('on_daily_todo', False):
            commitment = Commitment(
                user_id=current_user_id,
                task_id=new_item.id,
                entity_type='catchlist_item',
                due_date=date.today()
            )
            db.session.add(commitment)
            db.session.commit()
        
        # Return the new item with on_daily_todo status
        return jsonify({
            'id': new_item.id,
            'content': new_item.content,
            'created_at': new_item.created_at.isoformat(),
            'updated_at': new_item.updated_at.isoformat(),
            'status': new_item.status,
            'completed': new_item.completed,
            'completed_at': None,
            'on_daily_todo': data.get('on_daily_todo', False)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_items_bp.route('/api/catchlist-items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_catchlist_item(item_id):
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    item = CatchlistItem.query.filter_by(id=item_id, user_id=current_user_id).first()
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    if 'content' in data:
        item.content = data['content']
    
    if 'status' in data:
        item.status = data['status']
    
    if 'on_daily_todo' in data:
        # Check if there's already a commitment for today
        today = date.today()
        commitment = Commitment.query.filter_by(
            task_id=item.id,
            entity_type='catchlist_item',
            due_date=today
        ).first()
        
        if data['on_daily_todo'] and not commitment:
            # Create new commitment
            commitment = Commitment(
                user_id=current_user_id,
                task_id=item.id,
                entity_type='catchlist_item',
                due_date=today
            )
            db.session.add(commitment)
        elif not data['on_daily_todo'] and commitment:
            # Remove from today's list
            db.session.delete(commitment)
    
    try:
        db.session.commit()
        
        # Check if there's a commitment for today after our changes
        on_daily_todo = bool(Commitment.query.filter_by(
            task_id=item.id,
            entity_type='catchlist_item',
            due_date=date.today(),
            completed=False
        ).first())
        
        return jsonify({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
            'status': item.status,
            'completed': item.completed,
            'completed_at': item.completed_at.isoformat() if item.completed_at else None,
            'on_daily_todo': on_daily_todo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_items_bp.route('/api/catchlist-items/<int:item_id>/toggle-today', methods=['POST'])
@jwt_required()
def toggle_on_daily_todo(item_id):
    current_user_id = get_current_user_id()
    item = CatchlistItem.query.filter_by(id=item_id, user_id=current_user_id).first()
    
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    try:
        # Check if there's already a commitment for today
        today = date.today()
        commitment = Commitment.query.filter_by(
            task_id=item.id,
            entity_type='catchlist_item',
            due_date=today,
            completed=False
        ).first()
        
        if commitment:
            # Remove from today
            db.session.delete(commitment)
            on_daily_todo = False
        else:
            # Add to today
            commitment = Commitment(
                user_id=current_user_id,
                task_id=item.id,
                entity_type='catchlist_item',
                due_date=today
            )
            db.session.add(commitment)
            on_daily_todo = True
        
        db.session.commit()
        
        return jsonify({
            'id': item.id,
            'on_daily_todo': on_daily_todo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_items_bp.route('/api/catchlist-items/<int:item_id>/mark-done', methods=['POST'])
@jwt_required()
def mark_item_done(item_id):
    current_user_id = get_current_user_id()
    
    item = CatchlistItem.query.filter_by(id=item_id, user_id=current_user_id).first()
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    # Set completion status
    item.completed = True
    item.completed_at = datetime.utcnow()
    
    # If there's a commitment for today, mark it as completed
    today = date.today()
    commitment = Commitment.query.filter_by(
        task_id=item.id,
        entity_type='catchlist_item',
        due_date=today
    ).first()
    
    if commitment:
        commitment.completed = True
        commitment.completed_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Return points earned (we'll simulate this for now)
        points = 10  # Default points
        
        return jsonify({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
            'status': item.status,
            'completed': item.completed,
            'completed_at': item.completed_at.isoformat() if item.completed_at else None,
            'points': points  # Added for UI notification
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_items_bp.route('/api/catchlist-items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_catchlist_item(item_id):
    current_user_id = get_current_user_id()
    item = CatchlistItem.query.filter_by(id=item_id, user_id=current_user_id).first()
    
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    try:
        # Delete any commitments for this item
        Commitment.query.filter_by(
            task_id=item.id,
            entity_type='catchlist_item'
        ).delete()
        
        # Delete the item
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({"message": "Item deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500 