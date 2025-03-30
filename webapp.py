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

@app.route('/')
def home():
    # Get token from Authorization header
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    response = requests.get(f"{API_URL}/todos", headers=headers)
    if response.status_code == 200:
        todo_list = response.json()
    else:
        todo_list = []  # TODO make this return some kind of error
    return render_template("base.html", todo_list=todo_list)

@app.route("/add", methods=["POST"])
def add():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    title = request.form.get("title")
    response = requests.post(f"{API_URL}/todos", json={"title": title}, headers=headers)
    if response.status_code == 201:
        return redirect(url_for("home"))
    else:
        return "Failed to add todo", 500

@app.route("/update/<int:todo_id>")
def update(todo_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    response = requests.get(f"{API_URL}/todos/{todo_id}", headers=headers)
    if response.status_code == 200:
        todo = response.json()
        todo["complete"] = not todo["complete"]
        response = requests.put(f"{API_URL}/todos/{todo_id}", json=todo, headers=headers)
        if response.status_code == 200:
            return redirect(url_for("home"))
    return "Failed to update todo", 500

@app.route("/delete/<int:todo_id>", methods=["DELETE"])
def delete(todo_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    response = requests.delete(f"{API_URL}/todos/{todo_id}", headers=headers)
    if response.status_code == 200:
        return "", 204  # No Content response (DELETE success), reloading happens in javascript
    return "Failed to delete todo", 500

# We have to have a second ( __name__ == main ) check here
# because app.run() needs to happen after all routes are defined,
# meanwhile API_URL must be set before routes are defined.
if __name__ == "__main__":
    load_dotenv('environments/.env.local')
    app.run(debug=True, port=5000)