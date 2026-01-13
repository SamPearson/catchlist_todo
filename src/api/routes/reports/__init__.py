from flask import Blueprint
from . import reports, metric_types, templates

reports_bp = Blueprint('reports', __name__)

# Report Routes
reports_bp.add_url_rule('/api/reports', view_func=reports.list_reports, endpoint='list_reports', methods=['GET'])
reports_bp.add_url_rule('/api/reports', view_func=reports.create_report, endpoint='create_report', methods=['POST'])
reports_bp.add_url_rule('/api/reports/<int:report_id>', view_func=reports.get_report, endpoint='get_report', methods=['GET'])
reports_bp.add_url_rule('/api/reports/<int:report_id>', view_func=reports.update_report, endpoint='update_report', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/<int:report_id>', view_func=reports.delete_report, endpoint='delete_report', methods=['DELETE'])
reports_bp.add_url_rule('/api/reports/for-date', view_func=reports.get_or_create_for_date, endpoint='get_or_create_for_date', methods=['POST'])
reports_bp.add_url_rule('/api/reports/<int:report_id>/metrics', view_func=reports.get_report_metrics, endpoint='get_report_metrics', methods=['GET'])
reports_bp.add_url_rule('/api/reports/<int:report_id>/metrics', view_func=reports.set_report_metrics, endpoint='set_report_metrics', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/<int:report_id>/metrics/<int:metric_type_id>', view_func=reports.set_metric_value, endpoint='set_metric_value', methods=['PUT'])
reports_bp.add_url_rule('/api/reports/<int:report_id>/metrics/<int:metric_type_id>', view_func=reports.remove_metric_value, endpoint='remove_metric_value', methods=['DELETE'])

# Metric Type Routes
reports_bp.add_url_rule('/api/metric-types', view_func=metric_types.list_metric_types, endpoint='list_metric_types', methods=['GET'])
reports_bp.add_url_rule('/api/metric-types', view_func=metric_types.create_metric_type, endpoint='create_metric_type', methods=['POST'])
reports_bp.add_url_rule('/api/metric-types/<int:metric_type_id>', view_func=metric_types.get_metric_type, endpoint='get_metric_type', methods=['GET'])
reports_bp.add_url_rule('/api/metric-types/<int:metric_type_id>', view_func=metric_types.update_metric_type, endpoint='update_metric_type', methods=['PUT'])
reports_bp.add_url_rule('/api/metric-types/<int:metric_type_id>', view_func=metric_types.delete_metric_type, endpoint='delete_metric_type', methods=['DELETE'])
reports_bp.add_url_rule('/api/metric-types/<int:metric_type_id>/archive', view_func=metric_types.archive_metric_type, endpoint='archive_metric_type', methods=['POST'])
reports_bp.add_url_rule('/api/metric-types/<int:metric_type_id>/reactivate', view_func=metric_types.reactivate_metric_type, endpoint='reactivate_metric_type', methods=['POST'])

# Template Routes
reports_bp.add_url_rule('/api/report-templates', view_func=templates.list_templates, endpoint='list_templates', methods=['GET'])
reports_bp.add_url_rule('/api/report-templates', view_func=templates.create_template, endpoint='create_template', methods=['POST'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>', view_func=templates.get_template, endpoint='get_template', methods=['GET'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>', view_func=templates.update_template, endpoint='update_template', methods=['PUT'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>', view_func=templates.delete_template, endpoint='delete_template', methods=['DELETE'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>/set-default', view_func=templates.set_default_template, endpoint='set_default_template', methods=['POST'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>/metrics', view_func=templates.get_template_metrics, endpoint='get_template_metrics', methods=['GET'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>/metrics', view_func=templates.add_metric_to_template, endpoint='add_metric_to_template', methods=['POST'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>/metrics', view_func=templates.reorder_template_metrics, endpoint='reorder_template_metrics', methods=['PUT'])
reports_bp.add_url_rule('/api/report-templates/<int:template_id>/metrics/<int:metric_type_id>', view_func=templates.remove_metric_from_template, endpoint='remove_metric_from_template', methods=['DELETE'])
