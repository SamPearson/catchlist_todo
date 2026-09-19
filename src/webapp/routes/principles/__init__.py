from flask import Blueprint

principles_bp = Blueprint('principles', __name__, url_prefix='/principles')

from . import principle_handlers