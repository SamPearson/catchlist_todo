from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, current_app
import os
import requests
from dotenv import load_dotenv
import logging
from pathlib import Path
from .routes.reports import reports_bp
from ..config.db_setup import db
from ..config.db_config import Config

# Configure logging for production - only show warnings and errors
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Get the absolute path to the webapp directory
webapp_dir = Path(__file__).parent

# Initialize Flask with template and static folders
app = Flask(__name__,
            template_folder=str(webapp_dir / 'templates'),
            static_folder=str(webapp_dir / 'static'))

# Configure database
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Configure whether to show the demo page
app.config['SHOW_DEMO'] = os.getenv('SHOW_DEMO', 'True').lower() in ('true', '1', 't')

# Register blueprints
app.register_blueprint(reports_bp)

# env files are specified in systemd service files on staging&prod
# we launch the app with gunicon on staging/prod, thus ( __name__ == main ) only on dev/local.
# env file must be set here to get the API url, but the routes must be defined before running the app, so
# there's another if __name__ at the end of the script.
if __name__ == "__main__":
    env_path = Path(__file__).parent.parent / 'config' / 'environments' / '.env.local'
    load_dotenv(env_path)

API_URL = os.getenv('API_URL')
if not API_URL:
    logger.error("API_URL is not set. Please check your environment files.")

# Setup context processor to pass config to templates
@app.context_processor
def inject_globals():
    return {
        'show_demo': app.config['SHOW_DEMO'],
        'API_URL': API_URL
    }

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request from login form
    data = request.get_json()
    response = requests.post(f"{API_URL}/auth/login", json=data)
    
    if response.status_code == 200:
        api_response = response.json()
        # Create a response with the token cookie
        resp = make_response(jsonify(api_response))
        resp.set_cookie('auth_token', api_response.get('access_token', ''), httponly=False, path='/')
        return resp, response.status_code
    
    return jsonify(response.json()), response.status_code


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    try:
        response = requests.post(f"{API_URL}/auth/register", json=data)
        if response.status_code == 201:
            return jsonify(response.json()), response.status_code
        return jsonify({"message": "Registration failed"}), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during registration: {str(e)}")
        return jsonify({"message": "Failed to connect to API"}), 500


@app.route('/account')
def account():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))

    try:
        headers = {'Authorization': f'Bearer {token}'}
        # Get user info from API
        response = requests.get(f"{API_URL}/auth/user-info", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            return render_template(
                "account.html",
                username=user_info['username'],
                API_URL=API_URL
            )
    except Exception as e:
        logger.error(f"Error accessing account page: {str(e)}")

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    token = get_auth_token()
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        # Try to blacklist the token in the API
        requests.post(f"{API_URL}/auth/logout", headers=headers)

    # Clear the cookie whether the token blacklisting works or not
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('auth_token')
    return resp


def get_auth_token():
    """Get the auth token from headers or cookies"""
    # First try to get from headers
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        return token
    
    # Then try to get from cookies
    token = request.cookies.get('auth_token', '')
    if token:
        return token
    
    return ''





@app.route('/')
def home():
    token = get_auth_token()
    if not token:
        return render_template("landing.html")
    
    return redirect(url_for('desk'))


@app.route('/desk')
def desk():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    # We'll load all data via JavaScript on the client side
    return render_template("desk.html", API_URL=API_URL)


@app.route('/catchlist')
def catchlist():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    return render_template("catchlist.html", API_URL=API_URL)


@app.route('/projects')
def projects():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_URL}/projects", headers=headers)
        
        if response.status_code == 200:
            projects = response.json()
        else:
            projects = []
            
        return render_template("projects.html", projects=projects, API_URL=API_URL)
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        projects = []
        return render_template("projects.html", projects=projects, API_URL=API_URL)


@app.route('/routines')
def routines():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_URL}/routines", headers=headers)
        
        if response.status_code == 200:
            events = response.json()
        else:
            events = []
            
        return render_template("routines.html", events=events, API_URL=API_URL)
    except Exception as e:
        logger.error(f"Error fetching routines: {str(e)}")
        events = []
        return render_template("routines.html", events=events, API_URL=API_URL)


@app.route('/reports')
def reports():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    return render_template("reports.html", API_URL=API_URL)


@app.route('/demo')
def demo():
    # Check if demo is enabled
    if not app.config['SHOW_DEMO']:
        return redirect(url_for('home'))
    
    # The demo page doesn't require authentication
    return render_template("demo.html")


# We have to have a second ( __name__ == main ) check here
# because app.run() needs to happen after all routes are defined,
# meanwhile API_URL must be set before routes are defined.
# so no need to load the env file here, just run the app.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
