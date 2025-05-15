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

# Add the remaining catchlist routes (create, update, delete) 