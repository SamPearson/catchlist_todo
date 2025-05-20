from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required
import os

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/tags')
def tags():
    """Display the tags management page."""
    # Use our global get_auth_token function (defined in webapp.py)
    from src.webapp.webapp import get_auth_token, API_URL
    
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    return render_template('tags.html', API_URL=API_URL) 