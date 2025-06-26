from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)

from ..config.caldav_client import CalDAVClient

from ..config.models import db, User, BlacklistedToken
from ..config.db_config import initialize_database
from .app_factory import create_app
from .routes import auth, projects, routines, commitments, catchlist_items, tags
from .routes.reports import reports_bp  # Import new reports blueprint

app = create_app()

# Register all blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(reports_bp)

#Old blueprints
app.register_blueprint(projects.projects_bp, url_prefix='/api')
app.register_blueprint(routines.routines_bp)
app.register_blueprint(commitments.commitments_bp)
app.register_blueprint(catchlist_items.catchlist_items_bp)
app.register_blueprint(tags.tags_bp, url_prefix='/api/tags')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


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


@app.route('/api/auth/user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username
        })
    return jsonify({"message": "User not found"}), 404


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

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting account: {str(e)}")
        return jsonify({"message": f"Error deleting account: {str(e)}"}), 500


@app.route('/api/caldav/test-connection', methods=['POST'])
@jwt_required()
def test_caldav_connection():
    data = request.get_json()

    if not data or not data.get('url'):
        return jsonify({"success": False, "message": "CalDAV URL is required"}), 400

    url = data.get('url')
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    try:
        caldav_client = CalDAVClient(url, username, password)

        if not caldav_client.connect():
            return jsonify({
                "success": False, 
                "message": "Failed to connect to CalDAV server. Please check your credentials and URL."
            }), 400

        calendars = caldav_client.get_calendars()
        calendar_count = len(calendars)

        if calendar_count == 0:
            return jsonify({
                "success": False,
                "message": "Connected to server but no calendars found. Please check your permissions."
            }), 400

        # Try to get events from the first calendar
        first_calendar = calendars[0]
        events = caldav_client.get_events_as_dict(first_calendar)
        event_count = len(events)

        return jsonify({
            "success": True,
            "message": f"Successfully connected to CalDAV server. Found {calendar_count} calendars and {event_count} events in the first calendar.",
            "calendars": [cal.name for cal in calendars],
            "sample_events": events[:5] if events else []  # Return up to 5 sample events
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error connecting to CalDAV server: {str(e)}"
        }), 500


# Allows starting the server by running this script with the python3 command instead of flask or gunicorn commands
# only do this on local/dev. see README.md for more on server/prod vs local/dev
if __name__ == "__main__":
    initialize_database(app)  # handled in a config file when running on a server
    app.run(debug=True, port=5001)
