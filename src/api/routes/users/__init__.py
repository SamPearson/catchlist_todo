
from flask import Blueprint
from . import users

users_bp = Blueprint('users', __name__)

# Auth Routes
users_bp.add_url_rule('/api/auth/register', view_func=users.register, endpoint='register', methods=['POST'])
users_bp.add_url_rule('/api/auth/login', view_func=users.login, endpoint='login', methods=['POST'])
users_bp.add_url_rule('/api/auth/logout', view_func=users.logout, endpoint='logout', methods=['POST'])

# User Info Routes
users_bp.add_url_rule('/api/auth/user-info', view_func=users.get_user_info, endpoint='get_user_info', methods=['GET'])
users_bp.add_url_rule('/api/auth/user', view_func=users.update_user, endpoint='update_user', methods=['PUT'])

# Account Management Routes
users_bp.add_url_rule('/api/auth/change-password', view_func=users.change_password, endpoint='change_password', methods=['POST'])
users_bp.add_url_rule('/api/auth/delete-account', view_func=users.delete_account, endpoint='delete_account', methods=['POST'])