from flask import render_template
from datetime import datetime, timedelta
from . import sessions_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


def _get_today_range():
    """Returns start and end of today as ISO format strings (naive local time).

    The backend handles timezone conversion, so we just pass local times.
    """
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    return start.isoformat(), end.isoformat()


@sessions_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    start, end = _get_today_range()
    sessions = api_client.get('/api/sessions', token=token, params={'start': start, 'end': end}) or []

    # Sort most-recently-created first
    # Sorting here keeps the logic in one place and makes it easy to swap out
    sessions.sort(key=lambda t: t.get('created_at', ''), reverse=True)

    return render_template('pages/sessions/session_page.html', sessions=sessions)