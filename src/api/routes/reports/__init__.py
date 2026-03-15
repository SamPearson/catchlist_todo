
from flask import Blueprint
from . import reports

reports_bp = Blueprint('reports', __name__)

# Report Routes
reports_bp.add_url_rule('/api/reports', view_func=reports.list_reports, endpoint='list_reports', methods=['GET'])
reports_bp.add_url_rule('/api/reports/<int:report_id>', view_func=reports.get_report, endpoint='get_report', methods=['GET'])
reports_bp.add_url_rule('/api/reports/<int:report_id>', view_func=reports.update_report, endpoint='update_report', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/<int:report_id>', view_func=reports.delete_report, endpoint='delete_report', methods=['DELETE'])
reports_bp.add_url_rule('/api/reports/<string:kind>/<string:date>', view_func=reports.get_or_create_for_date, endpoint='get_or_create_for_date', methods=['GET'])