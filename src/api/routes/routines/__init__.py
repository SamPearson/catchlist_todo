from flask import Blueprint
from . import routines

routines_bp = Blueprint("routines", __name__)

routines_bp.add_url_rule("/api/routines", view_func=routines.list_routines, methods=["GET"])
routines_bp.add_url_rule("/api/routines", view_func=routines.create_routine, methods=["POST"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>", view_func=routines.get_routine, methods=["GET"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>", view_func=routines.update_routine, methods=["PATCH"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>", view_func=routines.delete_routine, methods=["DELETE"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>/sessions/generate",
                        view_func=routines.generate_routine_sessions,
                        methods=["POST"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>/sessions/future",
                        view_func=routines.delete_future_sessions,
                        methods=["DELETE"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>/sessions/past",
                        view_func=routines.delete_past_sessions,
                        methods=["DELETE"])