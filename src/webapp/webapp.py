from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, current_app
import os
from dotenv import load_dotenv
import logging
from pathlib import Path




logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Get the absolute path to the webapp directory
webapp_dir = Path(__file__).parent

# Initialize Flask with template and static folders
app = Flask(__name__,
            template_folder=str(webapp_dir / 'templates'),
            static_folder=str(webapp_dir / 'static'))


# env files are specified in systemd service files on staging&prod
# we launch the app with gunicon on staging/prod, thus ( __name__ == main ) only on dev/local.
# env file must be set here to get the API url, but the routes must be defined before running the app, so
# there's another if __name__ at the end of the script.
if __name__ == "__main__":
    env_path = Path(__file__).parent / 'config' / 'environments' / '.env.local'
    load_dotenv(env_path)

API_URL = os.getenv('API_URL')
if not API_URL:
    logger.error("API_URL is not set. Please check your environment files.")

# Setup context processor to pass config to templates
@app.context_processor
def inject_globals():
    return {
        'API_URL': API_URL
    }

# Register blueprints
from src.webapp.routes.auth import auth_bp
from src.webapp.routes.home import home_bp
from src.webapp.routes.demo import demo_bp

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)

# Only register demo blueprint in development
if os.getenv('FLASK_ENV') != 'production':
    app.register_blueprint(demo_bp)

# We have to have a second ( __name__ == main ) check here
# because app.run() needs to happen after all routes are defined,
# meanwhile API_URL must be set before routes are defined.
# so no need to load the env file here, just run the app.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
