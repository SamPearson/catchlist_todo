from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, Todo
from ..utils.helpers import get_current_user_id

todos_bp = Blueprint('todos', __name__)

@todos_bp.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    current_user_id = get_current_user_id()
    todos = Todo.query.filter_by(user_id=current_user_id).all()
    return jsonify([todo.as_dict() for todo in todos])

# Add the remaining todo routes 