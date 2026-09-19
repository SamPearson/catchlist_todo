from flask import render_template

from . import tags_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


@tags_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    tags = api_client.get('/api/tags', token=token) or []
    tags.sort(key=lambda t: t.get('created_at', ''), reverse=True)
    return render_template('pages/tags/tag_page.html', tags=tags)