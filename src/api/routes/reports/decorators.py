from functools import wraps
from flask import jsonify, request
from datetime import datetime

def validate_date_format(format_string):
    """Validate that the date parameter matches the expected format"""
    def decorator(f):
        @wraps(f)
        def decorated_function(date_str, *args, **kwargs):
            try:
                datetime.strptime(date_str, format_string)
            except ValueError:
                return jsonify({"error": f"Invalid date format. Use {format_string}"}), 400
            return f(date_str, *args, **kwargs)
        return decorated_function
    return decorator

def handle_report_errors(f):
    """Global error handler for report endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return decorated_function

def validate_json(required_fields=None):
    """Validate that the request contains JSON data with required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            # Check for required fields
            if required_fields:
                data = request.get_json()
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    }), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator
