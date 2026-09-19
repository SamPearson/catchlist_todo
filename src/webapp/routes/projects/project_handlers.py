from flask import render_template

from . import projects_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


@projects_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    projects = api_client.get(
        '/api/projects?include_completed=true&include_inactive=true',
        token=token
    ) or []
    projects.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    return render_template('pages/projects/project_page.html', projects=projects)