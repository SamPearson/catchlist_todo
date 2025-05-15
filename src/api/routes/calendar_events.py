from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, CalendarEvent, EventExecution
from ..utils.helpers import get_current_user_id

calendar_events_bp = Blueprint('calendar_events', __name__)

# Routes will be added here 