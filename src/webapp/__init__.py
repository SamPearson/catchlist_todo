from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .routes import auth, projects, routines, commitments, reports

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(routines.bp)
    app.register_blueprint(commitments.bp)
    app.register_blueprint(reports.bp)
    
    return app
