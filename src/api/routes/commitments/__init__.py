from flask import Blueprint
from . import commitments

commitments_bp = Blueprint("commitments", __name__)

commitments_bp.add_url_rule(
    "/api/commitments",
    view_func=commitments.list_commitments,
    endpoint="list_commitments",
    methods=["GET"],
)

commitments_bp.add_url_rule(
    "/api/commitments/<int:commitment_id>",
    view_func=commitments.get_commitment,
    endpoint="get_commitment",
    methods=["GET"],
)

commitments_bp.add_url_rule(
    "/api/commitments/<int:commitment_id>",
    view_func=commitments.delete_commitment,
    endpoint="delete_commitment",
    methods=["DELETE"],
)

commitments_bp.add_url_rule(
    "/api/commitments/hard",
    view_func=commitments.create_hard_commitment,
    endpoint="create_hard_commitment",
    methods=["POST"],
)

commitments_bp.add_url_rule(
    "/api/commitments/soft",
    view_func=commitments.create_soft_commitment,
    endpoint="create_soft_commitment",
    methods=["POST"],
)

commitments_bp.add_url_rule(
    "/api/commitments/<int:commitment_id>/status",
    view_func=commitments.update_commitment_status,
    endpoint="update_commitment_status",
    methods=["PUT"],
)