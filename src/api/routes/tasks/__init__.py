
from flask import Blueprint
from . import tasks

tasks_bp = Blueprint('tasks', __name__)

# Task Routes
tasks_bp.add_url_rule('/api/tasks', view_func=tasks.list_tasks, endpoint='list_tasks', methods=['GET'])
tasks_bp.add_url_rule('/api/tasks', view_func=tasks.create_task, endpoint='create_task', methods=['POST'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.get_task, endpoint='get_task', methods=['GET'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.update_task, endpoint='update_task', methods=['PUT'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.delete_task, endpoint='delete_task', methods=['DELETE'])

# Task State Management Routes
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/complete', view_func=tasks.complete_task, endpoint='complete_task', methods=['PATCH'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/uncomplete', view_func=tasks.uncomplete_task, endpoint='uncomplete_task', methods=['PATCH'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/activate', view_func=tasks.activate_task, endpoint='activate_task', methods=['PATCH'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/deactivate', view_func=tasks.deactivate_task, endpoint='deactivate_task', methods=['PATCH'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/status', view_func=tasks.change_task_status, endpoint='change_task_status', methods=['PATCH'])

# Task Project Association Routes
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/attach/<int:project_id>', view_func=tasks.attach_to_project, endpoint='attach_to_project', methods=['PATCH'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/detach', view_func=tasks.detach_from_project, endpoint='detach_from_project', methods=['PATCH'])

