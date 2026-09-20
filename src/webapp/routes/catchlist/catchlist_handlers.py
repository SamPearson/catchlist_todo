from flask import render_template

from . import catchlist_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


def render_catchlist_page():
    token = get_auth_token()
    catchlist = api_client.get('/api/catchlist', token=token) or {}
    return render_template(
        'pages/catchlist/catchlist_page.html',
        initial_content=catchlist.get('content', ''),
    )


@catchlist_bp.route('/')
@require_auth
def index():
    return render_catchlist_page()