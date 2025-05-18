from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import db, CatchlistItem, Commitment, Checkin
from ..utils.helpers import get_current_user_id
from datetime import datetime, date
from ..utils.commitment_utils import create_commitment_from_catchlist_item

catchlist_items_bp = Blueprint('catchlist_items', __name__)

@catchlist_items_bp.route('/api/catchlist-items', methods=['GET'])
@jwt_required()
def get_catchlist_items():
    current_user_id = get_current_user_id()
    
    # Check if we should include completed items
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    
    # Base query
    query = CatchlistItem.query.filter_by(user_id=current_user_id)
    
    # Filter out items with completed commitments unless explicitly requested
    if not show_completed:
        # Get items that have no completed commitments
        completed_commitments = db.session.query(Commitment.catchlist_item_id).filter(
            Commitment.user_id == current_user_id,
            Commitment.completed == True
        ).subquery()
        query = query.filter(~CatchlistItem.id.in_(completed_commitments))
    
    catchlist_items = query.all()
    
    return jsonify([{
        'id': item.id,
        'content': item.content,
        'created_at': item.created_at.isoformat(),
        'updated_at': item.updated_at.isoformat(),
        'status': item.status,
        'has_commitment_today': bool(Commitment.query.filter_by(
            catchlist_item_id=item.id,
            due_date=date.today(),
            completed=False
        ).first()),
        'is_completed': bool(Commitment.query.filter_by(
            catchlist_item_id=item.id,
            completed=True
        ).first())
    } for item in catchlist_items])

@catchlist_items_bp.route('/api/catchlist-items', methods=['POST'])
@jwt_required()
def create_catchlist_item():
    """Create a new catchlist item"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({"message": "Content is required"}), 400
    
    try:
        item = CatchlistItem(
            content=data.get('content'),
            user_id=user_id
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Create a commitment for the item if requested
        if data.get('add_to_today', False):
            create_commitment_from_catchlist_item(item, user_id)
        
        return jsonify(item.as_dict()), 201
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
    
    if 'add_to_today' in data:
        # Check if there's already a commitment for today
        today = date.today()
        commitment = Commitment.query.filter_by(
            catchlist_item_id=item.id,
            due_date=today
        ).first()
        
        if data['add_to_today'] and not commitment:
            # Create new commitment
            commitment = Commitment(
                user_id=current_user_id,
                catchlist_item_id=item.id,
                due_date=today
            )
            db.session.add(commitment)
        elif not data['add_to_today'] and commitment:
            # Remove from today's list
            db.session.delete(commitment)
    
    try:
        db.session.commit()
        
        # Check if there's a commitment for today after our changes
        has_commitment_today = bool(Commitment.query.filter_by(
            catchlist_item_id=item.id,
            due_date=date.today(),
            completed=False
        ).first())
        
        return jsonify({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
            'status': item.status,
            'has_commitment_today': has_commitment_today,
            'is_completed': bool(Commitment.query.filter_by(
                catchlist_item_id=item.id,
                completed=True
            ).first())
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@catchlist_items_bp.route('/api/catchlist-items/<int:item_id>/toggle-today', methods=['POST'])
@jwt_required()
def toggle_today(item_id):
    current_user_id = get_current_user_id()
    item = CatchlistItem.query.filter_by(id=item_id, user_id=current_user_id).first()
    
    if not item:
        return jsonify({"message": "Item not found"}), 404
    
    try:
        # Check if there's already a commitment for today
        today = date.today()
        commitment = Commitment.query.filter_by(
            catchlist_item_id=item.id,
            due_date=today,
            completed=False
        ).first()
        
        if commitment:
            # Remove from today
            db.session.delete(commitment)
            has_commitment_today = False
        else:
            # Add to today
            commitment = Commitment(
                user_id=current_user_id,
                catchlist_item_id=item.id,
                due_date=today
            )
            db.session.add(commitment)
            has_commitment_today = True
        
        db.session.commit()
        
        return jsonify({
            'id': item.id,
            'has_commitment_today': has_commitment_today
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
    
    # Find or create a commitment for today
    today = date.today()
    commitment = Commitment.query.filter_by(
        catchlist_item_id=item.id,
        due_date=today
    ).first()
    
    if not commitment:
        commitment = Commitment(
            user_id=current_user_id,
            catchlist_item_id=item.id,
            due_date=today
        )
        db.session.add(commitment)
    
    # Mark commitment as completed
    commitment.completed = True
    commitment.completed_at = datetime.now()
    
    # Create a checkin for this completion
    checkin = Checkin(
        user_id=current_user_id,
        entity_type='commitment',
        entity_id=commitment.id,
        content='Completed',
        completed=True
    )
    db.session.add(checkin)
    
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
            'is_completed': True,
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
            catchlist_item_id=item.id
        ).delete()
        
        # Delete the item
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({"message": "Item deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500 