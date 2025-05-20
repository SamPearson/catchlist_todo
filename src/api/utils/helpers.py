# Common helper functions used across routes
from flask_jwt_extended import get_jwt_identity

def get_current_user_id():
    """Get the current user ID from the JWT token"""
    return int(get_jwt_identity()) 