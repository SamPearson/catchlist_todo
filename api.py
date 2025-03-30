from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from db_models import db, Todo, User
from db_config import Config, initialize_database

app = Flask(__name__)
app.config.from_object(Config)
# Add JWT configuration
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
jwt = JWTManager(app)

# Add JWT error handlers
@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid token error: {error}")  # Debug log
    return jsonify({"msg": "Invalid token"}), 422

@jwt.unauthorized_loader
def unauthorized_callback(error):
    print(f"Unauthorized error: {error}")  # Debug log
    return jsonify({"msg": "Missing Authorization Header"}), 422

db.init_app(app)

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    print("Received registration request")  # Debug log
    data = request.get_json()
    print(f"Registration data: {data}")  # Debug log
    
    if not data or not data.get('username') or not data.get('password'):
        print("Missing username or password")  # Debug log
        return jsonify({"message": "Missing username or password"}), 400

    if User.query.filter_by(username=data['username']).first():
        print(f"Username {data['username']} already exists")  # Debug log
        return jsonify({"message": "Username already exists"}), 400

    try:
        user = User(username=data['username'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        print(f"Successfully created user: {data['username']}")  # Debug log
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print(f"Database error: {str(e)}")  # Debug log
        db.session.rollback()
        return jsonify({"message": "Database error occurred"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        # Convert user.id to string for the token
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        }), 200
    
    return jsonify({"message": "Invalid username or password"}), 401

# Modified todo endpoints to include authentication and user-specific data
@app.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    print("GET /api/todos - Received request")  # Debug log
    print(f"Request headers: {dict(request.headers)}")  # Debug log
    print(f"Request args: {dict(request.args)}")  # Debug log
    print(f"Request form: {dict(request.form)}")  # Debug log
    print(f"Request json: {request.get_json(silent=True)}")  # Debug log
    
    current_user_id = int(get_jwt_identity())  # Convert string ID to integer
    print(f"Current user ID: {current_user_id}")  # Debug log
    
    todos = Todo.query.filter_by(user_id=current_user_id).all()
    print(f"Found {len(todos)} todos for user {current_user_id}")  # Debug log
    return jsonify([todo.as_dict() for todo in todos])

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    current_user_id = int(get_jwt_identity())  # Convert string ID to integer
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
    if todo:
        return jsonify(todo.as_dict())
    return jsonify({"message": "Todo not found"}), 404

@app.route('/api/todos', methods=['POST'])
@jwt_required()
def create_todo():
    print("POST /api/todos - Received request")  # Debug log
    print(f"Request headers: {dict(request.headers)}")  # Debug log
    print(f"Request args: {dict(request.args)}")  # Debug log
    print(f"Request form: {dict(request.form)}")  # Debug log
    
    data = request.get_json()
    print(f"Request JSON data: {data}")  # Debug log
    
    current_user_id = int(get_jwt_identity())  # Convert string ID to integer
    print(f"Current user ID: {current_user_id}")  # Debug log
    
    try:
        new_todo = Todo(
            title=data.get('title'),
            complete=False,
            user_id=current_user_id
        )
        print(f"Created new todo object: {new_todo.as_dict()}")  # Debug log
        db.session.add(new_todo)
        db.session.commit()
        print("Successfully committed todo to database")  # Debug log
        return jsonify(new_todo.as_dict()), 201
    except Exception as e:
        print(f"Error creating todo: {str(e)}")  # Debug log
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    current_user_id = int(get_jwt_identity())  # Convert string ID to integer
    data = request.get_json()
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
    if todo:
        todo.title = data.get('title', todo.title)
        todo.complete = data.get('complete', todo.complete)
        db.session.commit()
        return jsonify(todo.as_dict())
    return jsonify({"message": "Todo not found"}), 404

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    current_user_id = int(get_jwt_identity())  # Convert string ID to integer
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": "Todo deleted"})
    return jsonify({"message": "Todo not found"}), 404

# Allows starting the server by running this script with the python3 command instead of flask or gunicorn commands
# only do this on local/dev. see README.md for more on server/prod vs local/dev
if __name__ == "__main__":
    initialize_database(app)  # handled in a config file when running on a server
    app.run(debug=True, port=5001)
