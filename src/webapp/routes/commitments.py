from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from ...config.models.commitment import Commitment, SoftCommitment
from ...config.models.time_blocks import TimeBlock
from src.database.db import db

commitments = Blueprint('commitments', __name__)


@commitments.route('/api/commitments/soft/<period>', methods=['GET'])
@login_required
def get_soft_commitments(period):
    """Get soft commitments for a specific time period"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start and end dates are required'}), 400
        
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
        
    commitments = SoftCommitment.query.filter(
        SoftCommitment.user_id == current_user.id,
        SoftCommitment.time_period == period,
        SoftCommitment.start_date >= start,
        SoftCommitment.end_date <= end
    ).all()
    
    return jsonify([c.as_dict() for c in commitments])

@commitments.route('/api/commitments/soft', methods=['POST'])
@login_required
def create_soft_commitment():
    """Create a new soft commitment"""
    data = request.get_json()
    
    required_fields = ['title', 'time_period', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
            
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
        
    commitment = SoftCommitment(
        user_id=current_user.id,
        title=data['title'],
        description=data.get('description'),
        time_period=data['time_period'],
        start_date=start_date,
        end_date=end_date,
        project_task_id=data.get('project_task_id'),
        catchlist_item_id=data.get('catchlist_item_id')
    )
    
    db.session.add(commitment)
    db.session.commit()
    
    return jsonify(commitment.as_dict()), 201

@commitments.route('/api/commitments/soft/<int:commitment_id>', methods=['PUT'])
@login_required
def update_soft_commitment(commitment_id):
    """Update a soft commitment"""
    commitment = SoftCommitment.query.filter_by(
        id=commitment_id,
        user_id=current_user.id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'title' in data:
        commitment.title = data['title']
    if 'description' in data:
        commitment.description = data['description']
    if 'completed' in data:
        commitment.completed = data['completed']
        commitment.completed_at = datetime.now() if data['completed'] else None
    if 'start_date' in data:
        commitment.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data:
        commitment.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    if 'project_task_id' in data:
        commitment.project_task_id = data['project_task_id']
    if 'catchlist_item_id' in data:
        commitment.catchlist_item_id = data['catchlist_item_id']
        
    commitment.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify(commitment.as_dict())

@commitments.route('/api/commitments/soft/<int:commitment_id>', methods=['DELETE'])
@login_required
def delete_soft_commitment(commitment_id):
    """Delete a soft commitment"""
    commitment = SoftCommitment.query.filter_by(
        id=commitment_id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(commitment)
    db.session.commit()
    
    return '', 204

@commitments.route('/commitments')
@jwt_required()
def index():
    return render_template('commitments/index.html')

@commitments.route('/commitments/today')
@jwt_required()
def today():
    return render_template('commitments/today.html')

@commitments.route('/api/commitments/<int:commitment_id>', methods=['PUT'])
@jwt_required()
def update_commitment(commitment_id):
    """Update a regular commitment"""
    commitment = Commitment.query.filter_by(
        id=commitment_id,
        user_id=get_jwt_identity()
    ).first_or_404()
    
    data = request.get_json()
    
    if 'completed' in data:
        commitment.completed = data['completed']
        commitment.completed_at = datetime.now() if data['completed'] else None
        
    db.session.commit()
    
    return jsonify(commitment.as_dict()) 