from flask import request
import logging
from functools import wraps
from flask import redirect, url_for

logger = logging.getLogger(__name__)


def get_auth_token():
    """Get the auth token from headers or cookies"""
    # First try to get from headers
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        return token

    # Then try to get from cookies
    token = request.cookies.get('auth_token', '')
    if token:
        return token

    return ''


def require_auth(f):
    """Decorator that checks for auth token and redirects to login if missing"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_auth_token()
        if not token:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function