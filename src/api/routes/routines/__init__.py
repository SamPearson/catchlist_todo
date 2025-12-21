from flask import Blueprint
from . import routines

routines_bp = Blueprint("routines", __name__)

routines_bp.add_url_rule("/api/routines", view_func=routines.list_routines, methods=["GET"])
routines_bp.add_url_rule("/api/routines", view_func=routines.create_routine, methods=["POST"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>", view_func=routines.get_routine, methods=["GET"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>", view_func=routines.update_routine, methods=["PUT"])
routines_bp.add_url_rule("/api/routines/<int:routine_id>", view_func=routines.delete_routine, methods=["DELETE"])

# CalDAV Import
routines_bp.add_url_rule("/api/routines/import", view_func=routines.import_routines, methods=["POST"])