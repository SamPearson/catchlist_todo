from datetime import datetime, date
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import Commitment, Checkin, db
from sqlalchemy import and_, or_

bp = Blueprint('commitments', __name__)

# Add OPTIONS method handler for CORS preflight requests
@bp.route('/api/commitments', methods=['OPTIONS'])
def options_commitments():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@bp.route('/api/commitments', methods=['POST'])
@jwt_required()
def create_commitment():
    """Create a new commitment"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('due_date'):
        return jsonify({"message": "Due date is required"}), 400
    
    # Create commitment
    commitment = Commitment(
        user_id=user_id,
        project_task_id=data.get('project_task_id'),
        catchlist_item_id=data.get('catchlist_item_id'),
        routine_id=data.get('routine_id'),
        session_id=data.get('session_id'),
        due_date=datetime.fromisoformat(data['due_date']).date(),
        start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None
    )
    
    try:
        db.session.add(commitment)
        db.session.commit()
        return jsonify(commitment.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@bp.route('/api/commitments/today', methods=['GET'])
@jwt_required()
def get_today_commitments():
    """Get all commitments due today for the current user"""
    user_id = get_jwt_identity()
    today = date.today()
    
    commitments = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.due_date == today
    ).all()
    
    return jsonify([commitment.as_dict() for commitment in commitments])

@bp.route('/api/commitments/<int:commitment_id>', methods=['PUT'])
@jwt_required()
def update_commitment(commitment_id):
    """Update a commitment's completion status"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    commitment = Commitment.query.filter(
        Commitment.id == commitment_id,
        Commitment.user_id == user_id
    ).first_or_404()
    
    if 'completed' in data:
        commitment.completed = data['completed']
        commitment.completed_at = datetime.utcnow() if data['completed'] else None
    
    db.session.commit()
    return jsonify(commitment.as_dict())

# Add OPTIONS method handler for checkins
@bp.route('/api/commitments/<int:commitment_id>/checkins', methods=['OPTIONS'])
def options_commitment_checkins(commitment_id):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@bp.route('/api/commitments/<int:commitment_id>/checkins', methods=['GET'])
@jwt_required()
def get_commitment_checkins(commitment_id):
    """Get all checkins for a commitment"""
    user_id = get_jwt_identity()
    
    # Verify commitment exists and belongs to user
    commitment = Commitment.query.filter(
        Commitment.id == commitment_id,
        Commitment.user_id == user_id
    ).first_or_404()
    
    checkins = Checkin.query.filter(
        Checkin.entity_id == commitment_id,
        Checkin.entity_type == 'commitment'
    ).order_by(Checkin.timestamp.desc()).all()
    
    return jsonify([checkin.as_dict() for checkin in checkins])

@bp.route('/api/commitments/<int:commitment_id>/checkins', methods=['POST'])
@jwt_required()
def add_commitment_checkin(commitment_id):
    """Add a new checkin to a commitment"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Verify commitment exists and belongs to user
    commitment = Commitment.query.filter(
        Commitment.id == commitment_id,
        Commitment.user_id == user_id
    ).first_or_404()
    
    checkin = Checkin(
        user_id=user_id,
        entity_type='commitment',
        entity_id=commitment_id,
        comment=data.get('comment'),
        rpe=data.get('rpe'),
        progress=data.get('progress'),
        mood=data.get('mood'),
        energy=data.get('energy')
    )
    
    db.session.add(checkin)
    db.session.commit()
    
    return jsonify(checkin.as_dict())

@bp.route('/api/commitments/search', methods=['GET'])
@jwt_required()
def search_commitments():
    """
    Search commitments with flexible criteria.
    Query parameters:
    - start_date: Start date for due_date range
    - end_date: End date for due_date range
    - completed: Filter by completion status
    - item_type: Filter by item type (project_task, catchlist_item)
    - has_checkins: Filter by presence of checkins
    - min_rpe: Minimum RPE in checkins
    - max_rpe: Maximum RPE in checkins
    - min_progress: Minimum progress in checkins
    - max_progress: Maximum progress in checkins
    """
    user_id = get_jwt_identity()
    query = Commitment.query.filter(Commitment.user_id == user_id)
    
    # Date range filter
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        query = query.filter(Commitment.due_date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(Commitment.due_date <= datetime.fromisoformat(end_date).date())
    
    # Completion status filter
    completed = request.args.get('completed')
    if completed is not None:
        query = query.filter(Commitment.completed == (completed.lower() == 'true'))
    
    # Item type filter
    item_type = request.args.get('item_type')
    if item_type:
        if item_type == 'project_task':
            query = query.filter(Commitment.project_task_id.isnot(None))
        elif item_type == 'catchlist_item':
            query = query.filter(Commitment.catchlist_item_id.isnot(None))
    
    # Checkin presence filter
    has_checkins = request.args.get('has_checkins')
    if has_checkins is not None:
        has_checkins = has_checkins.lower() == 'true'
        if has_checkins:
            query = query.filter(Commitment.checkins.any())
        else:
            query = query.filter(~Commitment.checkins.any())
    
    # RPE range filter
    min_rpe = request.args.get('min_rpe')
    max_rpe = request.args.get('max_rpe')
    if min_rpe or max_rpe:
        checkin_query = Checkin.query.filter(
            Checkin.entity_type == 'commitment',
            Checkin.entity_id == Commitment.id
        )
        if min_rpe:
            checkin_query = checkin_query.filter(Checkin.rpe >= int(min_rpe))
        if max_rpe:
            checkin_query = checkin_query.filter(Checkin.rpe <= int(max_rpe))
        query = query.filter(checkin_query.exists())
    
    # Progress range filter
    min_progress = request.args.get('min_progress')
    max_progress = request.args.get('max_progress')
    if min_progress or max_progress:
        checkin_query = Checkin.query.filter(
            Checkin.entity_type == 'commitment',
            Checkin.entity_id == Commitment.id
        )
        if min_progress:
            checkin_query = checkin_query.filter(Checkin.progress >= int(min_progress))
        if max_progress:
            checkin_query = checkin_query.filter(Checkin.progress <= int(max_progress))
        query = query.filter(checkin_query.exists())
    
    # Execute query and return results
    commitments = query.all()
    return jsonify([commitment.as_dict() for commitment in commitments])

@bp.route('/api/commitments', methods=['GET'])
@jwt_required()
def get_commitments():
    """Get commitments with optional filtering"""
    user_id = get_jwt_identity()
    query = Commitment.query.filter(Commitment.user_id == user_id)
    
    # Filter by catchlist item ID if provided
    catchlist_item_id = request.args.get('catchlist_item_id')
    if catchlist_item_id:
        query = query.filter(Commitment.catchlist_item_id == catchlist_item_id)
    
    commitments = query.order_by(Commitment.due_date.desc()).all()
    return jsonify([commitment.as_dict() for commitment in commitments]) 