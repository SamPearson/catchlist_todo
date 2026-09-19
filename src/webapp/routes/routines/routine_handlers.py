from flask import render_template

from . import routines_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


@routines_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    routines = api_client.get('/api/routines', token=token, params={'active_only': 'false'}) or []
    calendars = api_client.get('/api/calendars', token=token) or []
    routines.sort(key=lambda r: r.get('created_at', ''), reverse=True)
    return render_template('pages/routines/routine_page.html',
                           routines=routines, calendars=calendars)