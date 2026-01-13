from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.db import db
from src.database.reports.template_service import TemplateService, TemplateValidationError


def get_template_service():
    return TemplateService(db.session)


@jwt_required()
def get_template(template_id):
    """Get a specific template"""
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    return jsonify(template.as_dict()) if template else ('', 404)


@jwt_required()
def list_templates():
    """List all templates for the current user"""
    user_id = get_jwt_identity()
    timeframe_kind = request.args.get('kind')
    service = get_template_service()
    templates = service.list_templates(user_id, timeframe_kind=timeframe_kind)
    return jsonify([t.as_dict() for t in templates])


@jwt_required()
def create_template():
    """
    Create a new report template.

    Body:
    - name (required): Template name
    - timeframe_kind (required): day, week, month, season, year
    - is_default (optional): Set as default for this timeframe kind
    - metric_type_ids (optional): Array of metric type IDs to include
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    if 'name' not in data:
        return jsonify({'error': 'name is required'}), 400

    if 'timeframe_kind' not in data:
        return jsonify({'error': 'timeframe_kind is required'}), 400

    service = get_template_service()
    try:
        template = service.create_template(
            user_id=user_id,
            name=data['name'],
            timeframe_kind=data['timeframe_kind'],
            is_default=data.get('is_default', False),
            metric_type_ids=data.get('metric_type_ids')
        )
        return jsonify(template.as_dict()), 201
    except TemplateValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def update_template(template_id):
    """Update a template's name, timeframe_kind, or is_default"""
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    if not template:
        return ('', 404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    try:
        updated = service.update_template(template, data)
        return jsonify(updated.as_dict())
    except TemplateValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def delete_template(template_id):
    """Delete a template"""
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    if not template:
        return ('', 404)

    service.delete_template(template)
    return ('', 204)


@jwt_required()
def set_default_template(template_id):
    """Set a template as the default for its timeframe kind"""
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    if not template:
        return ('', 404)

    updated = service.set_default_template(template)
    return jsonify(updated.as_dict())


@jwt_required()
def get_template_metrics(template_id):
    """Get all metrics in a template"""
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    if not template:
        return ('', 404)

    metrics = service.get_template_metrics(template_id, user_id)
    return jsonify([m.as_dict() for m in metrics])


@jwt_required()
def add_metric_to_template(template_id):
    """
    Add a metric to a template.

    Body:
    - metric_type_id (required): ID of the metric type to add
    - sort_order (optional): Position in the template
    """
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    if not template:
        return ('', 404)

    data = request.get_json()
    if not data or 'metric_type_id' not in data:
        return jsonify({'error': 'metric_type_id is required'}), 400

    try:
        template_metric = service.add_metric_to_template(
            template=template,
            metric_type_id=data['metric_type_id'],
            user_id=user_id,
            sort_order=data.get('sort_order')
        )
        return jsonify(template_metric.as_dict()), 201
    except TemplateValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def remove_metric_from_template(template_id, metric_type_id):
    """Remove a metric from a template"""
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    if not template:
        return ('', 404)

    service.remove_metric_from_template(template, metric_type_id, user_id)
    return ('', 204)


@jwt_required()
def reorder_template_metrics(template_id):
    """
    Reorder metrics in a template.

    Body:
    - metric_type_ids (required): Array of metric type IDs in desired order
    """
    user_id = get_jwt_identity()
    service = get_template_service()
    template = service.get_template(template_id, user_id)
    if not template:
        return ('', 404)

    data = request.get_json()
    if not data or 'metric_type_ids' not in data:
        return jsonify({'error': 'metric_type_ids is required'}), 400

    if not isinstance(data['metric_type_ids'], list):
        return jsonify({'error': 'metric_type_ids must be an array'}), 400

    metrics = service.reorder_template_metrics(template, data['metric_type_ids'], user_id)
    return jsonify([m.as_dict() for m in metrics])