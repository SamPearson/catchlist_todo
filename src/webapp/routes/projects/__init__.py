from flask import Blueprint

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

from . import project_handlers