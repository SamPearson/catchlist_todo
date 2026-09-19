from flask import render_template

from . import principles_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


@principles_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    principles = api_client.get('/api/principles', token=token) or []
    principles.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    return render_template('pages/principles/principle_page.html', principles=principles)