from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database.backup.backup_service import BackupService, BackupValidationError
from src.database.db import db
from src.database.users.user_service import UserService
from src.database.users.user_repository import UserRepository

# Create single instances of the services
backup_service = BackupService(db.session)
user_service = UserService(UserRepository(db.session))


@jwt_required()
def export_data():
    """Export the current user's entire data set as a JSON blob"""
    current_user_id = int(get_jwt_identity())
    user = user_service.get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = backup_service.export_all(user)
    return jsonify(data), 200


@jwt_required()
def import_data():
    """Import a JSON blob, replacing the current user's entire data set"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    # Re-authenticate
    if not data or not data.get('password'):
        return jsonify({"message": "Password required for backup restore"}), 400

    user = user_service.get_user_by_id(current_user_id)
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid password"}), 401

    blob = data.get('data')
    if blob is None:
        return jsonify({"message": "Backup data is required"}), 400

    try:
        backup_service.import_replace(user, blob)
        return jsonify({"message": "Backup imported successfully"}), 200
    except BackupValidationError as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Backup import failed: {str(e)}"}), 500