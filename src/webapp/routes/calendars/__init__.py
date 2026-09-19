from flask import Blueprint

calendars_bp = Blueprint('calendars', __name__, url_prefix='/calendars')

from . import calendar_handlers