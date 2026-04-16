from flask import request, render_template, redirect, url_for, jsonify, make_response
from . import auth_bp
from src.webapp.services.auth import get_auth_token, require_auth
import os
import logging

logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['GET'])
def login():
    return render_template('pages/auth/login.html')


@auth_bp.route('/register', methods=['GET'])
def register():
    return render_template('pages/auth/register.html')


@auth_bp.route('/logout')
def logout():
    # Just clear the cookie and redirect - token blacklisting happens on API side if needed
    resp = make_response(redirect(url_for('home.index')))
    resp.delete_cookie('auth_token')
    return resp


@auth_bp.route('/account')
@require_auth
def account():
    return render_template('pages/auth/account.html')