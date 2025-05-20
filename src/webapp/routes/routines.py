from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('routines', __name__)

@bp.route('/routines')
@jwt_required()
def index():
    return render_template('routines/index.html')

@bp.route('/routines/<int:routine_id>')
@jwt_required()
def show(routine_id):
    return render_template('routines/show.html', routine_id=routine_id) 