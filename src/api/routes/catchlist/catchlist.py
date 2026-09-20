from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.catchlist.catchlist_service import CatchlistService, CatchlistValidationError
from src.database.db import db


@jwt_required()
def get_catchlist():
    """Get the current user's catch list."""
    user_id = get_jwt_identity()
    catchlist_service = CatchlistService(db.session)
    catchlist = catchlist_service.get_or_create(user_id=user_id)
    return jsonify(catchlist.as_dict())


@jwt_required()
def update_catchlist():
    """Replace the current user's catch list content."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    if 'content' not in data:
        return jsonify({'error': 'content is required'}), 400

    content = data.get('content')

    catchlist_service = CatchlistService(db.session)
    try:
        catchlist = catchlist_service.update_content(user_id=user_id, content=content)
        return jsonify(catchlist.as_dict())
    except CatchlistValidationError as e:
        return jsonify({'error': e.message}), 422