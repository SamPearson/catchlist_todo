from flask import redirect, render_template, url_for

from . import home_bp
from src.webapp.services.auth import get_auth_token
from src.webapp.routes.catchlist.catchlist_handlers import render_catchlist_page


@home_bp.route('/')
def index():
    token = get_auth_token()

    if token:
        # User is logged in - show the catch list at the root
        return render_catchlist_page()
    else:
        # User is not logged in - show landing page
        return render_template('pages/landing.html')


@home_bp.route('/desk')
def desk():
    token = get_auth_token()

    if token:
        # User is logged in - show the dashboard
        return render_template('pages/dashboard.html')
    else:
        # User is not logged in - send to the root (landing page)
        return redirect(url_for('home.index'))