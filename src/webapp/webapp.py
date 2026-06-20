from flask import Flask
import os
from dotenv import load_dotenv
import logging
from pathlib import Path


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

webapp_dir = Path(__file__).parent

app = Flask(__name__,
            template_folder=str(webapp_dir / 'templates'),
            static_folder=str(webapp_dir / 'static'))

# Setup context processor to pass API_URL to templates
@app.context_processor
def inject_globals():
    return {
        'API_URL': os.getenv('API_URL')
    }

from src.webapp.routes.auth import auth_bp
from src.webapp.routes.home import home_bp
from src.webapp.routes.demo import demo_bp
from src.webapp.routes.tasks import tasks_bp
from src.webapp.routes.sessions import sessions_bp

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(sessions_bp)

# Only register demo blueprint in development
if os.getenv('FLASK_ENV') != 'production':
    app.register_blueprint(demo_bp)

# This block only runs on dev; on staging and production we use gunicorn
if __name__ == "__main__":
    # Load an environment file to get the API URL (handled in service files on staging/prod)
    env_path = webapp_dir / 'config' / 'environments' / '.env.local'
    load_dotenv(env_path)
    logger.info(f"Loaded environment variables from {env_path}")
    logger.info(f"API URL: {os.getenv('API_URL')}")
    app.run(debug=True, port=5000)
