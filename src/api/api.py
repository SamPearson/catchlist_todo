from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from ..config.db_models import db, Todo, User, BlacklistedToken
from ..config.db_config import initialize_database
from .app_factory import create_app

app = create_app()


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing username or password"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400

    try:
        user = User()
        user.username = data['username']
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Database error occurred"}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        }), 200
    
    return jsonify({"message": "Invalid username or password"}), 401


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    token = BlacklistedToken(jti=jti)
    db.session.add(token)
    BlacklistedToken.clean_expired()
    db.session.commit()
    return jsonify({"message": "Successfully logged out"}), 200


def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = BlacklistedToken.query.filter_by(jti=jti).first()
    return token is not None


@app.route('/api/auth/delete-account', methods=['POST'])
@jwt_required()
def delete_account():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    # Re-authenticate
    if not data or not data.get('password'):
        return jsonify({"message": "Password required for account deletion"}), 400

    user = User.query.get(current_user_id)
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid password"}), 401

    try:
        # Get the JWT token ID for blacklisting
        jti = get_jwt()["jti"]
        # Blacklist the current token
        token = BlacklistedToken(jti=jti)
        db.session.add(token)

        # Delete the user (will cascade delete their todos thanks to our model setup)
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting account"}), 500


@app.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    current_user_id = int(get_jwt_identity())
    todos = Todo.query.filter_by(user_id=current_user_id).all()
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
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    try:
        new_todo = Todo(
            title=data.get('title'),
            complete=False,
            user_id=current_user_id
        )
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.as_dict()), 201
    except Exception as e:
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
