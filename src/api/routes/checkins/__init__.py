from flask import Blueprint
from . import checkins

checkins_bp = Blueprint("checkins", __name__)

checkins_bp.add_url_rule("/api/checkins/target", view_func=checkins.list_checkins, methods=["GET"])
checkins_bp.add_url_rule("/api/checkins", view_func=checkins.list_all_checkins, methods=["GET"])
checkins_bp.add_url_rule("/api/checkins", view_func=checkins.create_checkin, methods=["POST"])
checkins_bp.add_url_rule("/api/checkins/<int:checkin_id>", view_func=checkins.get_checkin, methods=["GET"])
checkins_bp.add_url_rule("/api/checkins/<int:checkin_id>",view_func=checkins.update_checkin,endpoint="update_checkin",methods=["PUT"])
checkins_bp.add_url_rule("/api/checkins/<int:checkin_id>", view_func=checkins.delete_checkin, methods=["DELETE"])