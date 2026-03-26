from flask import Blueprint
from . import calendars

calendars_bp = Blueprint("calendars", __name__)

calendars_bp.add_url_rule("/api/calendars", view_func=calendars.list_calendars, methods=["GET"])
calendars_bp.add_url_rule('/api/calendars/<int:calendar_id>', 'get_calendar', calendars.get_calendar, methods=['GET'])
calendars_bp.add_url_rule("/api/calendars", view_func=calendars.create_calendar, methods=["POST"])
calendars_bp.add_url_rule("/api/calendars/discover", view_func=calendars.discover_calendars, methods=["POST"])
calendars_bp.add_url_rule("/api/calendars/sync", view_func=calendars.sync_calendar, methods=["POST"])
calendars_bp.add_url_rule("/api/calendars/<int:calendar_id>", view_func=calendars.update_calendar, methods=["PATCH"])
calendars_bp.add_url_rule("/api/calendars/<int:calendar_id>/activate", view_func=calendars.activate_calendar, methods=["PATCH"])
calendars_bp.add_url_rule("/api/calendars/<int:calendar_id>/deactivate", view_func=calendars.deactivate_calendar, methods=["PATCH"])
calendars_bp.add_url_rule("/api/calendars/<int:calendar_id>", view_func=calendars.delete_calendar, methods=["DELETE"])
