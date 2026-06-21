from flask import render_template
from datetime import datetime
from . import reports_bp
from src.webapp.services.auth import require_auth, get_auth_token
from src.webapp.services.api_client import api_client


def _get_today_date():
    """Returns today's date as YYYY-MM-DD string."""
    return datetime.now().strftime('%Y-%m-%d')


@reports_bp.route('/')
@require_auth
def index():
    token = get_auth_token()
    today = _get_today_date()
    report = api_client.get(f'/api/reports/day/{today}', token=token, params={'full': True}) or {}

    return render_template('pages/reports/report_page.html', report=report)