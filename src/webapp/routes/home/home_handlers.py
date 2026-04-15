from flask import render_template
from . import home_bp
from src.webapp.services.auth import get_auth_token


@home_bp.route('/')
def index():
    token = get_auth_token()

    if token:
        # User is logged in - show dashboard/main app
        return render_template('pages/dashboard.html')
    else:
        # User is not logged in - show landing page
        return render_template('pages/landing.html')