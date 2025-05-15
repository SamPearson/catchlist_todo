from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import os
import requests
from dotenv import load_dotenv
import logging
from pathlib import Path

# Configure logging for production - only show warnings and errors
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
    env_path = Path(__file__).parent.parent / 'config' / 'environments' / '.env.local'
    load_dotenv(env_path)

API_URL = os.getenv('API_URL')
if not API_URL:
    logger.error("API_URL is not set. Please check your environment files.")


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


@app.route('/calendar')
def calendar():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))

    return render_template("calendar.html", API_URL=API_URL)


@app.route('/todos')
def todos():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_URL}/todos", headers=headers)
    
    if response.status_code == 200:
        todo_list = response.json()
        return render_template("todos.html", todo_list=todo_list, token=token)
    else:
        logger.error(f"Failed to fetch todos: {response.status_code}")
        return redirect(url_for('login'))


@app.route('/todos/<int:todo_id>')
def get_todo(todo_id):
    token = get_auth_token()
    if not token:
        return jsonify({"message": "Unauthorized"}), 401

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_URL}/todos/{todo_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return jsonify({"message": "Todo not found"}), response.status_code


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    token = get_auth_token()
    if not token:
        return jsonify({"message": "Unauthorized"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    data = request.get_json()
    
    # Ensure we're sending the right field names to the API
    update_data = {}
    if 'title' in data:
        update_data['title'] = data['title']
    if 'complete' in data:
        update_data['complete'] = data['complete']
    
    response = requests.put(f"{API_URL}/todos/{todo_id}", json=update_data, headers=headers)
    
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({"message": "Failed to update todo"}), response.status_code


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    token = get_auth_token()
    if not token:
        return jsonify({"message": "Unauthorized"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(f"{API_URL}/todos/{todo_id}", headers=headers)
    if response.status_code == 200:
        return "", 204  # No Content response (DELETE success), reloading happens in javascript
    return jsonify({"message": "Failed to delete todo"}), response.status_code

@app.route("/todos", methods=["POST"])
def add():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    headers = {'Authorization': f'Bearer {token}'}
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"message": "Title is required"}), 400
    
    # Ensure the data is in the format expected by the API
    todo_data = {
        "title": data['title'],
        "complete": data.get('complete', False)
    }
    
    response = requests.post(f"{API_URL}/todos", json=todo_data, headers=headers)
    
    if response.status_code == 201:
        return jsonify(response.json()), 201
    
    try:
        error_data = response.json()
        return jsonify({"message": error_data.get("message", "Failed to add todo")}), response.status_code
    except:
        return jsonify({"message": "Failed to add todo"}), response.status_code

@app.route('/')
def home():
    token = get_auth_token()
    if not token:
        return render_template("landing.html")
    
    return redirect(url_for('todos'))


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


@app.route('/calendar-events')
def calendar_events():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_URL}/calendar-events", headers=headers)
        
        if response.status_code == 200:
            events = response.json()
        else:
            events = []
            
        return render_template("calendar_events.html", events=events, API_URL=API_URL)
    except Exception as e:
        logger.error(f"Error fetching calendar events: {str(e)}")
        events = []
        return render_template("calendar_events.html", events=events, API_URL=API_URL)


@app.route('/today')
def today():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    # We'll load all data via JavaScript on the client side
    return render_template("today.html", API_URL=API_URL)


# We have to have a second ( __name__ == main ) check here
# because app.run() needs to happen after all routes are defined,
# meanwhile API_URL must be set before routes are defined.
# so no need to load the env file here, just run the app.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
