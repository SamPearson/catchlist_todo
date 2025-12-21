from flask import Blueprint
from . import principles

principles_bp = Blueprint("principles", __name__)

principles_bp.add_url_rule("/api/principles", view_func=principles.list_principles, methods=["GET"])
principles_bp.add_url_rule("/api/principles", view_func=principles.create_principle, methods=["POST"])
principles_bp.add_url_rule("/api/principles/<int:principle_id>", view_func=principles.get_principle, methods=["GET"])
principles_bp.add_url_rule("/api/principles/<int:principle_id>", view_func=principles.update_principle, methods=["PUT"])
principles_bp.add_url_rule("/api/principles/<int:principle_id>", view_func=principles.delete_principle, methods=["DELETE"])