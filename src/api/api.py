from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)



from src.api.utils.caldav_client import CalDAVClient

from src.database.config_db import initialize_database
from .app_factory import create_app

from .routes.tasks import tasks_bp
from .routes.projects import projects_bp
from .routes.tags import tags_bp
from .routes.reports import reports_bp
from .routes.timeframes import timeframes_bp
from .routes.commitments import commitments_bp
from .routes.checkins import checkins_bp
from .routes.routines import routines_bp
from .routes.sessions import sessions_bp
from .routes.calendars import calendars_bp
from .routes.principles import principles_bp
from .routes.users import users_bp

app = create_app()

# Register all blueprints
app.register_blueprint(users_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(tags_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(timeframes_bp)
app.register_blueprint(commitments_bp)
app.register_blueprint(checkins_bp)
app.register_blueprint(routines_bp)
app.register_blueprint(sessions_bp)
app.register_blueprint(calendars_bp)
app.register_blueprint(principles_bp)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200




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
