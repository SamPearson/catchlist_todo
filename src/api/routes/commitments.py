from datetime import datetime, date
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import Commitment, Checkin, db, ReportGenerator
from sqlalchemy import and_, or_

commitments_bp = Blueprint('commitments', __name__)

# Add OPTIONS method handler for CORS preflight requests
@commitments_bp.route('/api/commitments', methods=['OPTIONS'])
def options_commitments():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@commitments_bp.route('/api/commitments', methods=['POST'])
@jwt_required()
def create_commitment():
    """Create a new commitment"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields for hard commitments
    if not data.get('due_date'):
        return jsonify({"message": "Due date is required for hard commitments"}), 400
    
    # Parse the date string directly as YYYY-MM-DD
    year, month, day = map(int, data['due_date'].split('-'))
    due_date = date(year, month, day)
    
    # Create commitment
    commitment = Commitment(
        user_id=user_id,
        project_task_id=data.get('project_task_id'),
        catchlist_item_id=data.get('catchlist_item_id'),
        routine_id=data.get('routine_id'),
        session_id=data.get('session_id'),
        due_date=due_date,
        start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
        is_soft_commitment=False  # Explicitly set to False for hard commitments
    )
    
    try:
        db.session.add(commitment)
        db.session.commit()
        return jsonify(commitment.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@commitments_bp.route('/api/commitments/today', methods=['GET'])
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

@commitments_bp.route('/api/commitments/<int:commitment_id>', methods=['PUT'])
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
        commitment.completed_at = datetime.now() if data['completed'] else None
        
        # Generate reports after updating commitment
        ReportGenerator.generate_missing_reports(user_id, db.session)
    
    db.session.commit()
    return jsonify(commitment.as_dict())

@commitments_bp.route('/api/commitments/<int:commitment_id>', methods=['DELETE'])
@jwt_required()
def delete_commitment(commitment_id):
    """Delete a hard commitment"""
    user_id = get_jwt_identity()
    
    commitment = Commitment.query.filter(
        Commitment.id == commitment_id,
        Commitment.user_id == user_id,
        Commitment.is_soft_commitment == False
    ).first_or_404()
    
    try:
        db.session.delete(commitment)
        db.session.commit()
        return jsonify({"message": "Commitment deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

# Add OPTIONS method handler for checkins
@commitments_bp.route('/api/commitments/<int:commitment_id>/checkins', methods=['OPTIONS'])
def options_commitment_checkins(commitment_id):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@commitments_bp.route('/api/commitments/<int:commitment_id>/checkins', methods=['GET'])
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

@commitments_bp.route('/api/commitments/<int:commitment_id>/checkins', methods=['POST'])
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
    
    # Generate reports after adding checkin
    ReportGenerator.generate_missing_reports(user_id, db.session)
    
    return jsonify(checkin.as_dict())

@commitments_bp.route('/api/commitments/search', methods=['GET'])
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

@commitments_bp.route('/api/commitments', methods=['GET'])
@jwt_required()
def get_commitments():
    """Get commitments with optional filtering"""
    user_id = get_jwt_identity()
    query = Commitment.query.filter(Commitment.user_id == user_id)
    
    # Filter by catchlist item ID if provided
    catchlist_item_id = request.args.get('catchlist_item_id')
    if catchlist_item_id:
        query = query.filter(Commitment.catchlist_item_id == catchlist_item_id)
    
    # Filter by project task ID if provided
    project_task_id = request.args.get('project_task_id')
    if project_task_id:
        query = query.filter(Commitment.project_task_id == project_task_id)
    
    # Add logging
    print(f"Querying commitments for user {user_id}")
    if catchlist_item_id:
        print(f"Filtering by catchlist_item_id: {catchlist_item_id}")
    if project_task_id:
        print(f"Filtering by project_task_id: {project_task_id}")
    
    commitments = query.order_by(Commitment.due_date.desc()).all()
    print(f"Found {len(commitments)} commitments")
    
    return jsonify([commitment.as_dict() for commitment in commitments])

@commitments_bp.route('/api/commitments/range', methods=['OPTIONS'])
def options_commitments_range():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@commitments_bp.route('/api/commitments/range', methods=['GET'])
@jwt_required()
def get_commitments_range():
    """Get commitments within a date range"""
    user_id = get_jwt_identity()
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({"message": "Start date and end date are required"}), 400
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get all commitments within the date range
    commitments = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.due_date.between(start_date, end_date)
    ).order_by(Commitment.due_date.asc()).all()
    
    return jsonify([commitment.as_dict() for commitment in commitments])

# Add OPTIONS method handler for soft commitments
@commitments_bp.route('/api/commitments/soft/<period>', methods=['OPTIONS'])
def options_soft_commitments(period):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# Add a new OPTIONS handler for the base soft commitments endpoint
@commitments_bp.route('/api/commitments/soft', methods=['OPTIONS'])
def options_soft_commitments_base():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response

@commitments_bp.route('/api/commitments/soft/<period>', methods=['GET'])
@jwt_required()
def get_soft_commitments(period):
    """Get soft commitments for a specific time period"""
    user_id = get_jwt_identity()
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({"message": "Start and end dates are required"}), 400
    
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get soft commitments for the period
    commitments = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.is_soft_commitment == True,
        Commitment.time_period == period,
        Commitment.start_date >= start,
        Commitment.end_date <= end
    ).all()
    
    return jsonify([commitment.as_dict() for commitment in commitments])

# Add a new endpoint to get all soft commitments, with optional project_id filter
@commitments_bp.route('/api/commitments/soft', methods=['GET'])
@jwt_required()
def get_all_soft_commitments():
    """Get all soft commitments with optional filtering"""
    user_id = get_jwt_identity()
    
    # Base query for all soft commitments for the current user
    query = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.is_soft_commitment == True
    )
    
    # Apply project_id filter if provided
    project_id = request.args.get('project_id')
    if project_id:
        query = query.filter(Commitment.project_id == project_id)
    
    # Apply project_task_id filter if provided
    project_task_id = request.args.get('project_task_id')
    if project_task_id:
        query = query.filter(Commitment.project_task_id == project_task_id)
    
    # Apply catchlist_item_id filter if provided
    catchlist_item_id = request.args.get('catchlist_item_id')
    if catchlist_item_id:
        query = query.filter(Commitment.catchlist_item_id == catchlist_item_id)
    
    # Get all matching soft commitments
    commitments = query.order_by(Commitment.start_date.desc()).all()
    
    return jsonify([commitment.as_dict() for commitment in commitments])

@commitments_bp.route('/api/commitments/soft/<period>', methods=['POST'])
@jwt_required()
def create_soft_commitment(period):
    """Create a new soft commitment for a time period"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({"message": "Title is required"}), 400
    
    if not data.get('start_date') or not data.get('end_date'):
        return jsonify({"message": "Start and end dates are required"}), 400
    
    try:
        start_date = datetime.fromisoformat(data['start_date']).date()
        end_date = datetime.fromisoformat(data['end_date']).date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Create the commitment
    commitment = Commitment(
        user_id=user_id,
        title=data['title'],
        description=data.get('description') or data.get('notes'),
        start_date=start_date,
        end_date=end_date,
        due_date=None,  # Soft commitments don't have due dates
        is_soft_commitment=True,
        time_period=period,
        # Add item reference if provided
        project_id=data.get('project_id'),
        catchlist_item_id=data.get('catchlist_item_id'),
        project_task_id=data.get('project_task_id')
    )
    
    try:
        db.session.add(commitment)
        db.session.commit()
        return jsonify(commitment.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@commitments_bp.route('/api/commitments/soft/<int:commitment_id>', methods=['DELETE'])
@jwt_required()
def delete_soft_commitment(commitment_id):
    """Delete a soft commitment"""
    user_id = get_jwt_identity()
    
    commitment = Commitment.query.filter(
        Commitment.id == commitment_id,
        Commitment.user_id == user_id,
        Commitment.is_soft_commitment == True
    ).first_or_404()
    
    try:
        db.session.delete(commitment)
        db.session.commit()
        return jsonify({"message": "Soft commitment deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@commitments_bp.route('/api/commitments/current', methods=['OPTIONS'])
def options_current_commitments():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response

@commitments_bp.route('/api/commitments/current', methods=['GET'])
@jwt_required()
def get_current_commitments():
    """Get current commitments (due today or overdue)"""
    user_id = get_jwt_identity()
    today = date.today()
    
    # Get commitments due today or overdue
    commitments = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.due_date <= today,
        Commitment.completed == False
    ).order_by(Commitment.due_date.asc()).all()
    
    return jsonify([commitment.as_dict() for commitment in commitments])

@commitments_bp.route('/api/commitments/project-tasks', methods=['OPTIONS'])
def options_project_tasks():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response

@commitments_bp.route('/api/commitments/project-tasks', methods=['GET'])
@jwt_required()
def get_project_tasks():
    """Get all commitments associated with project tasks"""
    user_id = get_jwt_identity()
    
    # Get commitments that are associated with project tasks
    commitments = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.project_task_id.isnot(None)
    ).order_by(Commitment.due_date.asc()).all()
    
    return jsonify([commitment.as_dict() for commitment in commitments])

@commitments_bp.route('/api/commitments/catchlist-items', methods=['OPTIONS'])
def options_catchlist_items():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response

@commitments_bp.route('/api/commitments/catchlist-items', methods=['GET'])
@jwt_required()
def get_catchlist_items():
    """Get all commitments associated with catchlist items"""
    user_id = get_jwt_identity()
    
    # Get commitments that are associated with catchlist items
    commitments = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.catchlist_item_id.isnot(None)
    ).order_by(Commitment.due_date.asc()).all()
    
    return jsonify([commitment.as_dict() for commitment in commitments]) 