
from flask import Blueprint
from . import tasks

tasks_bp = Blueprint('tasks', __name__)

# Task Routes
tasks_bp.add_url_rule('/api/tasks', view_func=tasks.list_tasks, endpoint='list_tasks', methods=['GET'])
tasks_bp.add_url_rule('/api/tasks', view_func=tasks.create_task, endpoint='create_task', methods=['POST'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.get_task, endpoint='get_task', methods=['GET'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.update_task, endpoint='update_task', methods=['PUT'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.delete_task, endpoint='delete_task', methods=['DELETE'])