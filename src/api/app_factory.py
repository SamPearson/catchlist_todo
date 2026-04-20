from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import re

from src.database.db import db
from src.database.users.user_models import BlacklistedToken

from src.database.config_db import Config, initialize_database
from src.api.config.config import APIConfig


def create_app():
    app = Flask(__name__)
    
    # Load database configuration
    app.config.from_object(Config)
    
    # Load API configuration (JWT, CORS, etc.)
    app.config['JWT_SECRET_KEY'] = APIConfig.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = APIConfig.JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_TOKEN_LOCATION'] = APIConfig.JWT_TOKEN_LOCATION

    # Configure CORS to allow requests from the frontend
    CORS(app, 
        resources={r"/*": {
            "origins": APIConfig.CORS_ORIGINS,
            "methods": APIConfig.CORS_METHODS,
            "allow_headers": APIConfig.CORS_ALLOW_HEADERS,
            "supports_credentials": APIConfig.CORS_SUPPORTS_CREDENTIALS
        }})

    # initialize extensions
    db.init_app(app)

    # Initialize JWT
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = BlacklistedToken.query.filter_by(jti=jti).first()
        return token is not None

    # Add JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"msg": "Invalid token"}), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"msg": "Missing Authorization Header"}), 422

    with app.app_context():
        initialize_database(app)

    return app
