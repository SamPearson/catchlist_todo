from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.models import db, CatchListEntry, CatchlistExecution
from ..utils.helpers import get_current_user_id
from datetime import datetime, date

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
    
    # Track if on_daily_todo was changed
    was_on_daily = item.on_daily_todo
    
    if 'content' in data:
        item.content = data['content']
    
    if 'status' in data:
        item.status = data['status']
    
    if 'on_daily_todo' in data:
        item.on_daily_todo = data['on_daily_todo']
        
        # Create CatchlistExecution record when adding to today's list
        if item.on_daily_todo and not was_on_daily:
            today_date = date.today()
            # Check if there's already an execution for today
            existing_execution = CatchlistExecution.query.filter_by(
                catchlist_id=item.id,
                execution_date=today_date
            ).first()
            
            if not existing_execution:
                execution = CatchlistExecution(
                    catchlist_id=item.id,
                    user_id=current_user_id,
                    execution_date=today_date,
                    attempted=True,
                    completed=False
                )
                db.session.add(execution)
    
    try:
        db.session.commit()
        return jsonify({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': item.status,
            'on_daily_todo': item.on_daily_todo,
            'completed': item.completed
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
    
    # Set completion status
    item.completed = True
    item.completed_at = datetime.utcnow()
    item.on_daily_todo = False  # Remove from daily todo when completed
    
    # Update the CatchlistExecution record
    today_date = date.today()
    execution = CatchlistExecution.query.filter_by(
        catchlist_id=item.id,
        execution_date=today_date
    ).first()
    
    # If no execution record exists yet, create one
    if not execution:
        execution = CatchlistExecution(
            catchlist_id=item.id,
            user_id=current_user_id,
            execution_date=today_date,
            attempted=True
        )
        db.session.add(execution)
    
    # Mark as completed
    execution.completed = True
    
    try:
        db.session.commit()
        return jsonify({
            'id': item.id,
            'content': item.content,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': item.status,
            'completed': item.completed,
            'completed_at': item.completed_at.strftime('%Y-%m-%d %H:%M') if item.completed_at else None
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

@catchlist_bp.route('/api/catchlist/fix-dates', methods=['POST'])
@jwt_required()
def fix_catchlist_dates():
    current_user_id = get_current_user_id()
    
    try:
        # Find all completed catchlist items with future dates
        today = datetime.utcnow()
        
        items = CatchListEntry.query.filter(
            CatchListEntry.user_id == current_user_id,
            CatchListEntry.completed == True,
            CatchListEntry.completed_at > today
        ).all()
        
        updated_count = 0
        for item in items:
            item.completed_at = today
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully updated {updated_count} catchlist items",
            "updated_count": updated_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500 