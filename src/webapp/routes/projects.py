from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('projects', __name__)

@bp.route('/projects')
@jwt_required()
def index():
    return render_template('projects/index.html')

@bp.route('/projects/<int:project_id>')
@jwt_required()
def show(project_id):
    return render_template('projects/show.html', project_id=project_id) 