from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from ..config.db_models import db
from ..config.db_config import Config, initialize_database


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialize extensions
    db.init_app(app)

    # Add JWT configuration
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    jwt = JWTManager(app)

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
