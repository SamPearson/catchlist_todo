from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
from dotenv import load_dotenv

app = Flask(__name__)

# env files are specified in systemd service files on staging&prod
# we launch the app with gunicon on staging/prod, thus ( __name__ == main ) only on dev/local.
if __name__ == "__main__":
    load_dotenv('environments/.env.local')

API_URL = os.getenv('API_URL')
if not API_URL:
    print("API_URL is not set. Please check your environment files.")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request from login form
    data = request.get_json()
    response = requests.post(f"{API_URL}/auth/login", json=data)
    if response.status_code == 200:
        return jsonify(response.json()), response.status_code
    return jsonify(response.json()), response.status_code

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # Handle POST request from registration form
    data = request.get_json()
    print(f"Registration attempt with data: {data}")  # Debug log
    
    try:
        response = requests.post(f"{API_URL}/auth/register", json=data)
        print(f"API Response status: {response.status_code}")  # Debug log
        print(f"API Response text: {response.text}")  # Debug log
        
        if response.status_code == 201:
            return jsonify(response.json()), response.status_code
        else:
            # If the response isn't JSON, return a generic error
            return jsonify({"message": "Registration failed"}), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")  # Debug log
        return jsonify({"message": "Failed to connect to API"}), 500
    except ValueError as e:
        print(f"JSON decode error: {str(e)}")  # Debug log
        return jsonify({"message": "Invalid response from API"}), 500

@app.route('/logout')
def logout():
    # Clear the token from localStorage (handled by frontend)
    return redirect(url_for('login'))

def get_auth_token():
    """Get the auth token from headers, form data, or query parameters"""
    # Check headers first
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        return token
    
    # Then check form data
    token = request.form.get('Authorization', '').replace('Bearer ', '')
    if token:
        return token
    
    # Finally check query parameters
    token = request.args.get('token')
    if token:
        return token
    
    return None

@app.route('/api/todos')
def todos():
    token = get_auth_token()
    print(f"Token received: {'Yes' if token else 'No'}")  # Debug log
    print(f"Headers: {dict(request.headers)}")  # Debug log
    print(f"Form: {request.form}")  # Debug log
    print(f"Args: {request.args}")  # Debug log
    
    # If no token, redirect to login
    if not token:
        print("No token found, redirecting to login")  # Debug log
        return redirect(url_for('login'))
    
    # If token exists, show todo list
    headers = {'Authorization': f'Bearer {token}'}
    print(f"Sending request to API with token")  # Debug log
    response = requests.get(f"{API_URL}/todos", headers=headers)
    print(f"API response status: {response.status_code}")  # Debug log
    
    if response.status_code == 200:
        todo_list = response.json()
        print(f"Retrieved {len(todo_list)} todos")  # Debug log
    else:
        print(f"API error: {response.text}")  # Debug log
        todo_list = []  # TODO make this return some kind of error
    
    return render_template("todos.html", todo_list=todo_list)

@app.route('/api/todos/<int:todo_id>')
def get_todo(todo_id):
    token = get_auth_token()
    if not token:
        return jsonify({"message": "Unauthorized"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_URL}/todos/{todo_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return jsonify({"message": "Todo not found"}), response.status_code

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    token = get_auth_token()
    if not token:
        return jsonify({"message": "Unauthorized"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    data = request.get_json()
    response = requests.put(f"{API_URL}/todos/{todo_id}", json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    return jsonify({"message": "Failed to update todo"}), response.status_code

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    token = get_auth_token()
    if not token:
        return jsonify({"message": "Unauthorized"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(f"{API_URL}/todos/{todo_id}", headers=headers)
    if response.status_code == 200:
        return "", 204  # No Content response (DELETE success), reloading happens in javascript
    return jsonify({"message": "Failed to delete todo"}), response.status_code

@app.route("/api/todos", methods=["POST"])
def add():
    token = get_auth_token()
    if not token:
        return redirect(url_for('login'))
    
    headers = {'Authorization': f'Bearer {token}'}
    data = request.get_json()
    print(f"Received data: {data}")  # Debug log
    
    if not data or 'title' not in data:
        return jsonify({"message": "Title is required"}), 400
    
    # Send the title directly to the API
    response = requests.post(f"{API_URL}/todos", json={"title": data['title']}, headers=headers)
    print(f"API response status: {response.status_code}")  # Debug log
    print(f"API response text: {response.text}")  # Debug log
    
    if response.status_code == 201:
        return redirect(url_for("todos"))
    else:
        try:
            error_data = response.json()
            return jsonify({"message": error_data.get("message", "Failed to add todo")}), response.status_code
        except:
            return jsonify({"message": "Failed to add todo"}), response.status_code

@app.route('/')
def home():
    token = get_auth_token()
    
    # If no token, show landing page
    if not token:
        return render_template('landing.html')
    
    # If token exists, redirect to todos page with the token
    return redirect(url_for('todos', token=token))

# We have to have a second ( __name__ == main ) check here
# because app.run() needs to happen after all routes are defined,
# meanwhile API_URL must be set before routes are defined.
if __name__ == "__main__":
    load_dotenv('environments/.env.local')
    app.run(debug=True, port=5000)