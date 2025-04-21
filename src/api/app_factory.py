from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from ..config.db_models import db, BlacklistedToken
from ..config.db_config import Config, initialize_database


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Without CORS, the webapp and api can't connect when run locally,
    # as they run on different ports, and that makes them two different places.
    CORS(app)

    # initialize extensions
    db.init_app(app)

    # Add JWT configuration
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
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
