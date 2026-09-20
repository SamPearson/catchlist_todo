from flask import Blueprint

catchlist_bp = Blueprint('catchlist', __name__, url_prefix='/catchlist')

from . import catchlist_handlers