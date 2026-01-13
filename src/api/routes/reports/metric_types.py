from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.db import db
from src.database.reports.metric_type_service import MetricTypeService, MetricTypeValidationError


def get_metric_type_service():
    return MetricTypeService(db.session)


@jwt_required()
def get_metric_type(metric_type_id):
    """Get a specific metric type"""
    user_id = get_jwt_identity()
    service = get_metric_type_service()
    metric_type = service.get_metric_type(metric_type_id, user_id)
    return jsonify(metric_type.as_dict()) if metric_type else ('', 404)


@jwt_required()
def list_metric_types():
    """List all metric types for the current user"""
    user_id = get_jwt_identity()
    include_archived = request.args.get('include_archived', '').lower() == 'true'
    service = get_metric_type_service()
    metric_types = service.list_metric_types(user_id, include_archived=include_archived)
    return jsonify([mt.as_dict() for mt in metric_types])


@jwt_required()
def create_metric_type():
    """
    Create a new metric type.

    Body:
    - name (required): Display name
    - value_type (required): integer, float, rating, boolean
    - unit (optional): Label for display (e.g., "hours", "1-10")
    - min_value (optional): Minimum valid value (for rating type)
    - max_value (optional): Maximum valid value (for rating type)
    - sort_order (optional): Default display ordering
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    if 'name' not in data:
        return jsonify({'error': 'name is required'}), 400

    if 'value_type' not in data:
        return jsonify({'error': 'value_type is required'}), 400

    service = get_metric_type_service()
    try:
        metric_type = service.create_metric_type(
            user_id=user_id,
            name=data['name'],
            value_type=data['value_type'],
            data=data
        )
        return jsonify(metric_type.as_dict()), 201
    except MetricTypeValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def update_metric_type(metric_type_id):
    """Update a metric type"""
    user_id = get_jwt_identity()
    service = get_metric_type_service()
    metric_type = service.get_metric_type(metric_type_id, user_id)
    if not metric_type:
        return ('', 404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    try:
        updated = service.update_metric_type(metric_type, data)
        return jsonify(updated.as_dict())
    except MetricTypeValidationError as e:
        return jsonify({'error': e.message}), 400


@jwt_required()
def delete_metric_type(metric_type_id):
    """
    Hard delete a metric type.
    Warning: This cascades to all MetricValues using this type.
    Prefer archive_metric_type to preserve historical data.
    """
    user_id = get_jwt_identity()
    service = get_metric_type_service()
    metric_type = service.get_metric_type(metric_type_id, user_id)
    if not metric_type:
        return ('', 404)

    service.delete_metric_type(metric_type)
    return ('', 204)


@jwt_required()
def archive_metric_type(metric_type_id):
    """Archive a metric type (soft delete)"""
    user_id = get_jwt_identity()
    service = get_metric_type_service()
    metric_type = service.get_metric_type(metric_type_id, user_id)
    if not metric_type:
        return ('', 404)

    archived = service.archive_metric_type(metric_type)
    return jsonify(archived.as_dict())


@jwt_required()
def reactivate_metric_type(metric_type_id):
    """Reactivate an archived metric type"""
    user_id = get_jwt_identity()
    service = get_metric_type_service()
    metric_type = service.get_metric_type(metric_type_id, user_id)
    if not metric_type:
        return ('', 404)

    reactivated = service.reactivate_metric_type(metric_type)
    return jsonify(reactivated.as_dict())