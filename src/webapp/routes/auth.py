from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    return render_template('auth/login.html')

@bp.route('/register')
def register():
    return render_template('auth/register.html')

@bp.route('/logout')
@jwt_required()
def logout():
    return redirect(url_for('auth.login')) 