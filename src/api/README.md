# API Layer

## Overview

The API layer provides RESTful HTTP endpoints for the productivity management system. It follows a clear architectural pattern:

- **Routes**: HTTP endpoint definitions and request/response handling
- **Services**: Business logic and data validation (in database layer)
- **Authentication**: JWT-based user authentication with token blacklisting

**Golden Rule**: Route handlers validate request **shape** and handle HTTP concerns. Service layer validates data **legitimacy** and enforces business rules.

## Documentation

The docs directory contains more thorough documentation for the API, database entities, and more.
It's in zim wiki format; only limited pages are duplicated into MD files.

**API Route documentation can be found in `docs/wiki/API/Routes/`**

This README covers architectural patterns and implementation guidelines. For detailed endpoint specifications, request/response examples, and route-specific documentation, refer to the wiki.

## Directory Structure

    api/
    ├── routes/
    │   ├── users/
    │   │   ├── __init__.py        # Blueprint registration
    │   │   └── users.py           # Route handlers
    │   ├── tasks/
    │   │   ├── __init__.py
    │   │   └── tasks.py
    │   ├── projects/
    │   │   ├── __init__.py
    │   │   └── projects.py
    │   └── [other entities...]
    ├── utils/
    │   ├── helpers.py             # Shared utility functions
    │   └── caldav_client.py       # CalDAV integration
    ├── api.py                     # Application entry point & blueprint registration
    ├── app_factory.py             # Flask app configuration & initialization
    └── README.md

**Note**: Each route directory contains a blueprint definition in `__init__.py` and route handlers in `{entity}.py`.

## Request Flow

1. Client sends HTTP request with JWT token (if authenticated endpoint)
2. Flask-JWT-Extended validates token and checks blacklist
3. Flask routes to appropriate blueprint
4. Route handler validates request shape (required fields, data types)
5. Route handler calls service layer with validated data
6. Service layer validates business rules and data legitimacy
7. Service layer interacts with repository for database operations
8. Response formatted and returned to client

## Application Architecture

### App Factory Pattern

The application uses a factory pattern for flexibility and testability:
```
python
# app_factory.py
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS
    CORS(app, resources={...})
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configure JWT
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return BlacklistedToken.query.filter_by(jti=jti).first() is not None
    
    # Initialize database
    with app.app_context():
        initialize_database(app)
    
    return app
```
**Key Features:**
- CORS configured for local development (ports 5000/5001)
- JWT tokens can be revoked via blacklist
- Database initialized on app creation
- Extension initialization within app context

### Blueprint Registration

Blueprints are registered in `api.py`:
```
python
from .app_factory import create_app
from .routes.tasks import tasks_bp
from .routes.projects import projects_bp
# ... other blueprints

app = create_app()

app.register_blueprint(users_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(projects_bp)
# ... register other blueprints
```
This centralizes all route registration for easy discovery and management.

## Authentication

### JWT Token Authentication

Protected routes require a JWT token in the Authorization header:

    Authorization: Bearer <token>

### Token Lifecycle

**Getting a Token:**

    POST /api/login
    Content-Type: application/json

    {
      "username": "user1",
      "password": "securepassword"
    }

**Response:**

    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "user": {
        "id": 1,
        "username": "user1",
        "name": "User One",
        "timezone": "America/New_York"
      }
    }

**Using the Token:**

    GET /api/tasks
    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

**Logging Out (Blacklisting Token):**

    POST /api/logout
    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Adds the token's JTI (JWT ID) to the blacklist, preventing further use.

### Protected Routes

Use the `@jwt_required()` decorator for endpoints requiring authentication:
```
python
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def list_tasks():
    """List all tasks for the current user"""
    user_id = get_jwt_identity()
    # ... handler logic
```
**Important:** Always extract `user_id` from the JWT token, never trust client-provided user IDs.

### Token Configuration

Configured in `database/config_db.py`:
- **JWT_SECRET_KEY**: Secret for signing tokens (must be set in environment)
- **JWT_TOKEN_LOCATION**: Tokens accepted in headers and cookies
- Token expiration handled via `Config.get_token_expires_delta()`

## Endpoint Patterns

### Standard CRUD Endpoints

Most user-owned resources follow this pattern:

    GET    /api/{entity}              # List all for current user
    POST   /api/{entity}              # Create new for current user
    GET    /api/{entity}/<id>         # Get one (owned by current user)
    PUT    /api/{entity}/<id>         # Update one (owned by current user)
    DELETE /api/{entity}/<id>         # Delete one (owned by current user)

**All require authentication** and are automatically scoped to the current user.

### Example: Tasks

Standard CRUD:

    GET    /api/tasks                 # List tasks
    POST   /api/tasks                 # Create task
    GET    /api/tasks/123             # Get task
    PUT    /api/tasks/123             # Update task
    DELETE /api/tasks/123             # Delete task

Domain-specific state management:

    PATCH  /api/tasks/123/complete    # Mark as complete
    PATCH  /api/tasks/123/uncomplete  # Mark as incomplete
    PATCH  /api/tasks/123/activate    # Set active=true
    PATCH  /api/tasks/123/deactivate  # Set active=false
    PATCH  /api/tasks/123/status      # Change status

Relationship management:

    PATCH  /api/tasks/123/attach/456  # Attach to project 456
    PATCH  /api/tasks/123/detach      # Detach from project

This pattern separates general updates (PUT) from specific state transitions (PATCH).

### Query Parameters

**Filtering:**

    GET /api/tasks?include_completed=true

**Pagination (when implemented):**

    GET /api/tasks?page=1&limit=20

**Sorting (when implemented):**

    GET /api/tasks?sort=created_at&order=desc

Route handlers extract query parameters and pass to service layer.

## Response Formats

### Success Responses

**Single Entity (200 OK):**
```
json
{
  "id": 1,
  "title": "Complete documentation",
  "description": "Write API layer README",
  "completed": false,
  "status": "open",
  "active": true,
  "user_id": 1,
  "project_id": null,
  "created_at": "2024-01-15T10:30:00-05:00",
  "updated_at": "2024-01-15T10:30:00-05:00",
  "tags": [],
  "principles": []
}
```
**List of Entities (200 OK):**
```
json
[
  {
    "id": 1,
    "title": "Task one",
    "completed": false,
    "..."
  },
  {
    "id": 2,
    "title": "Task two",
    "completed": true,
    "..."
  }
]
```
**Creation (201 Created):**
```
json
{
  "id": 1,
  "title": "New task",
  "..."
}
```
**Deletion (204 No Content):**

Empty response body with 204 status.

### Error Responses

**Validation Error (400 Bad Request):**
```
json
{
  "error": "Title is required"
}
```
**Not Found (404 Not Found):**

Empty response body with 404 status.

**Unauthorized (401/422):**
```
json
{
  "msg": "Missing Authorization Header"
}
```

```
json
{
  "msg": "Invalid token"
}
```
**Service Validation Error (400 Bad Request):**
```
json
{
  "error": "Task title cannot be empty"
}
```
### Standard HTTP Status Codes

- **200 OK** - Successful GET, PUT, PATCH
- **201 Created** - Successful POST (resource created)
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Invalid request data/format
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Authenticated but not authorized
- **404 Not Found** - Resource doesn't exist or not owned by user
- **422 Unprocessable Entity** - JWT validation errors
- **500 Internal Server Error** - Server-side error

## Blueprint Structure

### Blueprint Definition

Each entity has a blueprint defined in `routes/{entity}/__init__.py`:
```
python
# routes/tasks/__init__.py
from flask import Blueprint
from . import tasks

tasks_bp = Blueprint('tasks', __name__)

# CRUD Routes
tasks_bp.add_url_rule('/api/tasks', view_func=tasks.list_tasks, endpoint='list_tasks', methods=['GET'])
tasks_bp.add_url_rule('/api/tasks', view_func=tasks.create_task, endpoint='create_task', methods=['POST'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.get_task, endpoint='get_task', methods=['GET'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.update_task, endpoint='update_task', methods=['PUT'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>', view_func=tasks.delete_task, endpoint='delete_task', methods=['DELETE'])

# State Management Routes
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/complete', view_func=tasks.complete_task, endpoint='complete_task', methods=['PATCH'])
tasks_bp.add_url_rule('/api/tasks/<int:task_id>/uncomplete', view_func=tasks.uncomplete_task, endpoint='uncomplete_task', methods=['PATCH'])
# ... additional routes
```
**Benefits:**
- Clear separation between route registration and handlers
- Explicit URL patterns and HTTP methods
- Named endpoints for URL generation
- Easy to see all routes for an entity at a glance

### Route Handlers

Route handlers are defined in `routes/{entity}/{entity}.py`:
```
python
# routes/tasks/tasks.py
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.tasks.task_service import TaskService, TaskValidationError
from src.database.tasks.task_repository import TaskRepository
from src.database.db import db

# Create a single instance of the service
task_service = TaskService(TaskRepository(db.session))

@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    return jsonify(task.as_dict()) if task else ('', 404)

@jwt_required()
def create_task():
    """Create a new task"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate request shape
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        task = task_service.create_task(
            user_id=user_id,
            title=data['title'],
            data=data
        )
        return jsonify(task.as_dict()), 201
    except TaskValidationError as e:
        return jsonify({'error': e.message}), 400
```
**Pattern:**
1. Extract user ID from JWT token
2. Validate request shape (required fields present)
3. Call service layer with validated data
4. Handle service exceptions and return appropriate responses
5. Use `as_dict()` for model serialization

## Adding New Endpoints

Follow these steps to add endpoints for a new entity (e.g., `Note`):

### 1. Create Route Directory

    api/routes/notes/
    ├── __init__.py
    └── notes.py

### 2. Define Blueprint and URL Rules
```
python
# api/routes/notes/__init__.py
from flask import Blueprint
from . import notes

notes_bp = Blueprint('notes', __name__)

# CRUD endpoints
notes_bp.add_url_rule('/api/notes', view_func=notes.list_notes, endpoint='list_notes', methods=['GET'])
notes_bp.add_url_rule('/api/notes', view_func=notes.create_note, endpoint='create_note', methods=['POST'])
notes_bp.add_url_rule('/api/notes/<int:note_id>', view_func=notes.get_note, endpoint='get_note', methods=['GET'])
notes_bp.add_url_rule('/api/notes/<int:note_id>', view_func=notes.update_note, endpoint='update_note', methods=['PUT'])
notes_bp.add_url_rule('/api/notes/<int:note_id>', view_func=notes.delete_note, endpoint='delete_note', methods=['DELETE'])
```
### 3. Implement Route Handlers
```
python
# api/routes/notes/notes.py
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.notes.note_service import NoteService, NoteValidationError
from src.database.notes.note_repository import NoteRepository
from src.database.db import db

note_service = NoteService(NoteRepository(db.session))

@jwt_required()
def list_notes():
    """List all notes for the current user"""
    user_id = get_jwt_identity()
    notes = note_service.list_notes(user_id=user_id)
    return jsonify([note.as_dict() for note in notes])

@jwt_required()
def get_note(note_id):
    """Get a specific note"""
    user_id = get_jwt_identity()
    note = note_service.get_note(note_id=note_id, user_id=user_id)
    return jsonify(note.as_dict()) if note else ('', 404)

@jwt_required()
def create_note():
    """Create a new note"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        note = note_service.create_note(user_id=user_id, data=data)
        return jsonify(note.as_dict()), 201
    except NoteValidationError as e:
        return jsonify({'error': e.message}), 400

@jwt_required()
def update_note(note_id):
    """Update a note"""
    user_id = get_jwt_identity()
    note = note_service.get_note(note_id=note_id, user_id=user_id)
    if not note:
        return ('', 404)
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400
    
    try:
        updated_note = note_service.update_note(note, data)
        return jsonify(updated_note.as_dict())
    except NoteValidationError as e:
        return jsonify({'error': e.message}), 400

@jwt_required()
def delete_note(note_id):
    """Delete a note"""
    user_id = get_jwt_identity()
    note = note_service.get_note(note_id=note_id, user_id=user_id)
    if not note:
        return ('', 404)
    
    note_service.delete_note(note)
    return ('', 204)
```
### 4. Register Blueprint
```
python
# api/api.py
from .routes.notes import notes_bp

app.register_blueprint(notes_bp)
```
### 5. Document Routes

Add detailed route documentation to `docs/wiki/API/Routes/` following the existing pattern.

## Common Patterns

### Service Instantiation

Create a single service instance at module level:
```
python
# At top of route handler file
task_service = TaskService(TaskRepository(db.session))

# Use in handlers
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    # ...
```
This ensures consistent service behavior across all handlers.

### Error Handling

Handle service-specific exceptions:
```
python
try:
    task = task_service.create_task(user_id=user_id, title=data['title'], data=data)
    return jsonify(task.as_dict()), 201
except TaskValidationError as e:
    return jsonify({'error': e.message}), 400
```
Let unexpected errors bubble up for global error handling.

### Optional Query Parameters

Extract with defaults:
```
python
@jwt_required()
def list_tasks():
    user_id = get_jwt_identity()
    include_completed = request.args.get('include_completed', '').lower() == 'true'
    tasks = task_service.list_tasks(user_id=user_id, include_completed=include_completed)
    return jsonify([task.as_dict() for task in tasks])
```
### State Transition Endpoints

For domain-specific state changes, use dedicated endpoints:
```
python
@jwt_required()
def complete_task(task_id):
    """Mark a task as completed. Query param toggle=true toggles completion instead."""
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    if not task:
        return ('', 404)
    
    try:
        toggle = request.args.get('toggle', 'false').lower() == 'true'
        
        if toggle:
            completed_task = task_service.toggle_task_completion(task)
        else:
            completed_task = task_service.complete_task(task)
        
        return jsonify(completed_task.as_dict())
    except TaskValidationError as e:
        return jsonify({'error': e.message}), 400
```
This makes the API more expressive and self-documenting.

### Relationship Management

Use descriptive endpoint names for relationship operations:
```
python
@jwt_required()
def attach_to_project(task_id, project_id):
    """Attach a task to a project"""
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    if not task:
        return ('', 404)
    
    try:
        attached_task = task_service.attach_to_project(task, project_id, user_id=user_id)
        db.session.commit()
        return jsonify(attached_task.as_dict())
    except TaskValidationError as e:
        return jsonify({'error': e.message}), 400
```
## Timezone Handling

All timestamps are stored in UTC and converted to user's timezone for responses:
```
python
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id=task_id, user_id=user_id)
    if not task:
        return ('', 404)
    
    # User's timezone is retrieved from their profile
    # as_dict() handles conversion automatically
    return jsonify(task.as_dict(user_timezone=user.timezone))
```
The `as_dict()` method in models handles timezone conversion using the `from_utc()` utility.

## CORS Configuration

Configured in `app_factory.py` for local development:
```
python
CORS(app, 
    resources={r"/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }})
```
**For production:** Update `origins` to match your frontend domain.

## Best Practices

### DO

- ✅ Use `@jwt_required()` for all user-scoped endpoints
- ✅ Extract user ID from JWT with `get_jwt_identity()`, never trust client
- ✅ Validate request shape in route handlers (required fields present)
- ✅ Use service layer for all business logic and validation
- ✅ Return appropriate HTTP status codes
- ✅ Use `as_dict()` for model serialization
- ✅ Handle service exceptions explicitly
- ✅ Create single service instance per module
- ✅ Use descriptive endpoint names
- ✅ Document route handlers with docstrings
- ✅ Document routes in `docs/wiki/API/Routes/`

### DON'T

- ❌ Access repositories directly from routes
- ❌ Put business logic in route handlers
- ❌ Trust user-provided user IDs (always use JWT)
- ❌ Skip request validation
- ❌ Return raw exception messages to clients
- ❌ Expose sensitive information in errors
- ❌ Mix authentication logic with business logic
- ❌ Forget to commit database session when needed
- ❌ Use mutable default arguments in Python functions
- ❌ Skip timezone handling for timestamps

## Running the API

### Local Development

    python3 src/api/api.py

Runs on `http://localhost:5001` with debug mode enabled.

### Production Deployment

For production deployment instructions, see `infrastructure/README.md`.

## Configuration

### Database Configuration

Database settings are in `database/config_db.py`:
- Database URI
- SQLAlchemy configuration
- JWT configuration
- Token expiration settings

### Environment Variables

Required environment variables:
- **JWT_SECRET_KEY**: Secret for signing JWT tokens (must be secure in production)

Optional:
- **DATABASE_URL**: Override default SQLite database location

## Health Check

The API includes a health check endpoint:

    GET /api/health

**Response (200 OK):**
```
json
{
  "status": "healthy"
}
```
Use this for monitoring and load balancer health checks.

## Further Reading

For detailed implementation examples, refer to:
- `routes/tasks/` - Complete CRUD with state management and relationships
- `routes/projects/` - Entity with one-to-many relationships
- `routes/users/` - Authentication endpoints
- `app_factory.py` - Application initialization and configuration
- `docs/wiki/API/Routes/` - Detailed route documentation
