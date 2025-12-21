from flask import Blueprint
from . import sessions

sessions_bp = Blueprint("sessions", __name__)

sessions_bp.add_url_rule("/api/sessions", view_func=sessions.list_sessions, methods=["GET"])
sessions_bp.add_url_rule("/api/routines/<int:routine_id>/sessions", view_func=sessions.create_session, methods=["POST"])
sessions_bp.add_url_rule("/api/sessions/<int:session_id>", view_func=sessions.get_session, methods=["GET"])
sessions_bp.add_url_rule("/api/sessions/<int:session_id>", view_func=sessions.update_session, methods=["PUT"])
sessions_bp.add_url_rule("/api/sessions/<int:session_id>", view_func=sessions.delete_session, methods=["DELETE"])