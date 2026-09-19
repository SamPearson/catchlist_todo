from flask import render_template

from . import calendars_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


@calendars_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    calendars = api_client.get('/api/calendars', token=token, params={'include_inactive': 'true'}) or []
    calendars.sort(key=lambda c: c.get('created_at', ''), reverse=True)
    return render_template('pages/calendars/calendar_page.html', calendars=calendars)