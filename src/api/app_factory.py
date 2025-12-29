from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import re

from src.database.db import db
from src.database.users.user import BlacklistedToken

from src.database.config_db import Config, initialize_database


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure CORS to allow requests from the frontend
    CORS(app, 
        resources={r"/*": {
            "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
            "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True
        }})

    # initialize extensions
    db.init_app(app)

    # Add JWT configuration
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
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
