from flask import Blueprint, render_template, redirect, url_for, request
from src.webapp.services.auth import require_auth
from src.webapp.services.api_client import api_client

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks')
@require_auth
def task_list():
    """Tasks list page"""
    include_completed = request.args.get('include_completed', '').lower() == 'true'
    tasks = api_client.get("/tasks", params={'include_completed': include_completed})
    return render_template('tasks/task_list.html', tasks=tasks)


@tasks_bp.route('/tasks', methods=['POST'])
@require_auth
def create_task():
    """Handle task creation via form submission"""
    data = {
        'content': request.form.get('content')
    }
    api_client.post('/tasks', data)
    return redirect(url_for('tasks.task_list'))


@tasks_bp.route('/tasks/<task_id>', methods=['POST'])
@require_auth
def handle_task(task_id):
    """Handle task updates and deletions via form submission"""
    method = request.form.get('_method', '').upper()

    if method == 'PUT':
        # Handle task update
        completed = request.form.get('completed') == 'true'
        data = {
            'completed': completed
        }
        api_client.put(f'/tasks/{task_id}', data)

    elif method == 'DELETE':
        # Handle task deletion
        api_client.delete(f'/tasks/{task_id}')

    return redirect(url_for('tasks.task_list'))
