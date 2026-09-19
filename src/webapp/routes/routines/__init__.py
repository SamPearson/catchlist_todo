from flask import Blueprint

routines_bp = Blueprint('routines', __name__, url_prefix='/routines')

from . import routine_handlers