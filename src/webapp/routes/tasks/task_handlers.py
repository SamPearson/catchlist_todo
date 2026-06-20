from flask import render_template
from . import tasks_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


@tasks_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    tasks = api_client.get('/api/tasks', token=token) or []

    # Sort most-recently-created first
    # Sorting here keeps the logic in one place and makes it easy to swap out
    tasks.sort(key=lambda t: t.get('created_at', ''), reverse=True)

    return render_template('pages/tasks/task_page.html', tasks=tasks)