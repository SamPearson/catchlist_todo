from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.db_models import db, CalendarEvent, EventExecution, ProjectSubtask
from ..utils.helpers import get_current_user_id

today_bp = Blueprint('today', __name__)

# Routes will be added here 