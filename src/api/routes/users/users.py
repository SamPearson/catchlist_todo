from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from src.database.users.user_service import UserService, UserValidationError
from src.database.users.user_repository import UserRepository
from src.database.users.user_models import BlacklistedToken
from src.database.db import db

# Create a single instance of the service
user_service = UserService(UserRepository(db.session))


def register():
    """Register a new user"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing username or password"}), 400

    try:
        user = user_service.register_user(
            username=data['username'],
            password=data['password'],
            name=data.get('name'),
            timezone=data.get('timezone', 'UTC')
        )
        return jsonify({"message": "User created successfully", "user": user.as_dict()}), 201
    except UserValidationError as e:
        return jsonify({"message": e.message}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Database error occurred"}), 500


def login():
    """Login a user"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing username or password"}), 400

    user = user_service.authenticate_user(data['username'], data['password'])

    if user:
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.as_dict()
        }), 200

    return jsonify({"message": "Invalid username or password"}), 401


@jwt_required()
def logout():
    """Logout a user by blacklisting their token"""
    jti = get_jwt()['jti']
    token = BlacklistedToken(jti=jti)
    db.session.add(token)
    BlacklistedToken.clean_expired()
    db.session.commit()
    return jsonify({"message": "Successfully logged out"}), 200


@jwt_required()
def get_user_info():
    """Get the current user's information"""
    current_user_id = int(get_jwt_identity())
    user = user_service.get_user_by_id(current_user_id)

    if user:
        return jsonify(user.as_dict()), 200

    return jsonify({"message": "User not found"}), 404


@jwt_required()
def update_user():
    """Update the current user's information"""
    current_user_id = int(get_jwt_identity())
    user = user_service.get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No update data provided"}), 400

    try:
        updated_user = user_service.update_user(user, data)
        return jsonify(updated_user.as_dict()), 200
    except UserValidationError as e:
        return jsonify({"message": e.message}), 400


@jwt_required()
def change_password():
    """Change the current user's password"""
    current_user_id = int(get_jwt_identity())
    user = user_service.get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({"message": "Both old_password and new_password are required"}), 400

    try:
        user_service.change_password(user, data['old_password'], data['new_password'])
        return jsonify({"message": "Password changed successfully"}), 200
    except UserValidationError as e:
        return jsonify({"message": e.message}), 400


@jwt_required()
def delete_account():
    """Delete the current user's account"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    # Re-authenticate
    if not data or not data.get('password'):
        return jsonify({"message": "Password required for account deletion"}), 400

    user = user_service.get_user_by_id(current_user_id)
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid password"}), 401

    try:
        # Get the JWT token ID for blacklisting
        jti = get_jwt()["jti"]
        # Blacklist the current token
        token = BlacklistedToken(jti=jti)
        db.session.add(token)

        # Delete the user (service handles cascade deletes)
        user_service.delete_user(user)

        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting account: {str(e)}"}), 500