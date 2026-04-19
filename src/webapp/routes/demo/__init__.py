from flask import Blueprint

demo_bp = Blueprint('demo', __name__, url_prefix='/component-demo')

from . import component_demo_handlers