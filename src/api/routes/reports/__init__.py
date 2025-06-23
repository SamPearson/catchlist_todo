from flask import Blueprint
from . import day_reports, week_reports, month_reports, season_reports, year_reports

reports_bp = Blueprint('reports', __name__)

# Day Report Routes
reports_bp.add_url_rule('/api/reports/day/<date>', view_func=day_reports.get_report, endpoint='day_get_report', methods=['GET'])
reports_bp.add_url_rule('/api/reports/day', view_func=day_reports.list_reports, endpoint='day_list_reports', methods=['GET'])
reports_bp.add_url_rule('/api/reports/day', view_func=day_reports.create_report, endpoint='day_create_report', methods=['POST'])
reports_bp.add_url_rule('/api/reports/day/<date>/get_or_create', view_func=day_reports.get_or_create_report, endpoint='day_get_or_create_report', methods=['GET'])
reports_bp.add_url_rule('/api/reports/day/<int:report_id>', view_func=day_reports.update_report, endpoint='day_update_report', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/day/<int:report_id>', view_func=day_reports.delete_report, endpoint='day_delete_report', methods=['DELETE'])

# Week Report Routes
reports_bp.add_url_rule('/api/reports/week/<date>', view_func=week_reports.get_report, endpoint='week_get_report', methods=['GET'])
reports_bp.add_url_rule('/api/reports/week', view_func=week_reports.list_reports, endpoint='week_list_reports', methods=['GET'])
reports_bp.add_url_rule('/api/reports/week', view_func=week_reports.create_report, endpoint='week_create_report', methods=['POST'])
reports_bp.add_url_rule('/api/reports/week/<int:report_id>', view_func=week_reports.update_report, endpoint='week_update_report', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/week/<int:report_id>', view_func=week_reports.delete_report, endpoint='week_delete_report', methods=['DELETE'])

# Month Report Routes
reports_bp.add_url_rule('/api/reports/month/<date>', view_func=month_reports.get_report, endpoint='month_get_report', methods=['GET'])
reports_bp.add_url_rule('/api/reports/month', view_func=month_reports.list_reports, endpoint='month_list_reports', methods=['GET'])
reports_bp.add_url_rule('/api/reports/month', view_func=month_reports.create_report, endpoint='month_create_report', methods=['POST'])
reports_bp.add_url_rule('/api/reports/month/<int:report_id>', view_func=month_reports.update_report, endpoint='month_update_report', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/month/<int:report_id>', view_func=month_reports.delete_report, endpoint='month_delete_report', methods=['DELETE'])

# Season Report Routes
reports_bp.add_url_rule('/api/reports/season/<date>', view_func=season_reports.get_report, endpoint='season_get_report', methods=['GET'])
reports_bp.add_url_rule('/api/reports/season/<int:year>/<string:season>', view_func=season_reports.get_report_by_year_season, endpoint='season_get_report_by_year_season', methods=['GET'])
reports_bp.add_url_rule('/api/reports/season', view_func=season_reports.list_reports, endpoint='season_list_reports', methods=['GET'])
reports_bp.add_url_rule('/api/reports/season', view_func=season_reports.create_report, endpoint='season_create_report', methods=['POST'])
reports_bp.add_url_rule('/api/reports/season/<int:report_id>', view_func=season_reports.update_report, endpoint='season_update_report', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/season/<int:report_id>', view_func=season_reports.delete_report, endpoint='season_delete_report', methods=['DELETE'])

# Year Report Routes
reports_bp.add_url_rule('/api/reports/year/<date>', view_func=year_reports.get_report, endpoint='year_get_report_by_date', methods=['GET'])
reports_bp.add_url_rule('/api/reports/year/<int:year>', view_func=year_reports.get_report_by_year, endpoint='year_get_report_by_year', methods=['GET'])
reports_bp.add_url_rule('/api/reports/year', view_func=year_reports.list_reports, endpoint='year_list_reports', methods=['GET'])
reports_bp.add_url_rule('/api/reports/year', view_func=year_reports.create_report, endpoint='year_create_report', methods=['POST'])
reports_bp.add_url_rule('/api/reports/year/<int:report_id>', view_func=year_reports.update_report, endpoint='year_update_report', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/year/<int:report_id>', view_func=year_reports.delete_report, endpoint='year_delete_report', methods=['DELETE'])
