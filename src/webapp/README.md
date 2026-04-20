# Webapp Layer

## Overview

The webapp provides a server-side rendered web interface for the productivity management system with client-side interactivity. It communicates with a separate API service for all data operations.

**Technology Stack:**
- **Backend**: Python 3.10.12, Flask
- **Frontend**: Bulma CSS, Alpine.js, Font Awesome
- **Architecture**: Server-side rendering with client-side interactivity
- **Authentication**: JWT token authentication via cookies

**Current Status:** The webapp is in a proof-of-concept phase. While the API is feature-complete, the webapp is being built incrementally with a focus on creating reusable UI components and component demos.

## Directory Structure

    webapp/
    ├── routes/                      # Route blueprints
    │   ├── auth/                    # Authentication routes
    │   │   ├── __init__.py          # Blueprint registration
    │   │   └── auth_handlers.py    # Route handler functions
    │   ├── home/                    # Home/landing routes
    │   │   ├── __init__.py
    │   │   └── home_handlers.py
    │   └── demo/                    # UI component demos (dev only)
    │       ├── __init__.py
    │       └── component_demo_handlers.py
    ├── services/                    # Shared services
    │   ├── api_client.py            # Server-side API client
    │   └── auth.py                  # Auth utilities and decorators
    ├── templates/                   # Jinja2 templates
    │   ├── base.html                # Base layout template
    │   ├── components/              # Reusable UI components
    │   │   ├── navbar.html
    │   │   └── tasks/               # Task-related components
    │   │       ├── task_create.html
    │   │       ├── task_edit.html
    │   │       ├── task_item.html
    │   │       ├── task_manager.html
    │   │       └── task_search.html
    │   └── pages/                   # Full page templates
    │       ├── auth/                # Authentication pages
    │       │   ├── login.html
    │       │   ├── register.html
    │       │   └── account.html
    │       ├── component_demo/      # Component demo pages
    │       │   ├── component_demo.html
    │       │   └── task_component_demo.html
    │       ├── landing.html         # Landing page
    │       └── dashboard.html       # Main dashboard
    ├── static/                      # Static assets
    │   ├── js/
    │   │   └── api_helper.js        # Client-side API utilities
    │   └── images/
    └── webapp.py                    # Main Flask application

## Component-Based Development

The webapp follows a component-based approach where UI elements are built as reusable, self-contained pieces.

### Component Structure

Components live in `templates/components/` organized by feature:

    templates/components/
    ├── navbar.html
    └── tasks/
        ├── task_create.html
        ├── task_edit.html
        ├── task_item.html
        ├── task_manager.html
        └── task_search.html

Each component is:
- **Self-contained**: Includes its own Alpine.js logic
- **Reusable**: Can be included in multiple pages
- **Testable**: Has a corresponding demo page

### Component Demos

Every component(group) has a demo page in `templates/pages/component_demo/` for development and testing:
```
html
<!-- templates/pages/component_demo/task_component_demo.html -->
{% extends "base.html" %}

{% block title %}Task Components Demo{% endblock %}

{% block content %}
<section class="section">
    <div class="container">
        <h1 class="title">Task Components</h1>
        
        <div class="box">
            <h2 class="subtitle">Task Manager</h2>
            {% include 'components/tasks/task_manager.html' %}
        </div>
        
        <div class="box">
            <h2 class="subtitle">Task Create Form</h2>
            {% include 'components/tasks/task_create.html' %}
        </div>
    </div>
</section>
{% endblock %}
```
**Benefits:**
- Test components in isolation
- Validate component behavior without building full features
- Provide visual reference for component library
- Debug component logic without page complexity
- Potential to set up pages for complex selenium tests without involving api calls or database interactions 

**Note:** Component demo routes are only registered in non-production environments.

## API Communication

The webapp communicates with a separate API service running on port 5001. There are two API clients for different contexts:

### Server-Side API Client (Python)

**Location:** `services/api_client.py`

**Purpose:** Used by Flask route handlers to fetch data before rendering templates.

**Usage:**
```
python
from src.webapp.services.api_client import api_client
from src.webapp.services.auth import require_auth, get_auth_token

@some_bp.route('/example')
@require_auth
def example():
    token = get_auth_token()
    data = api_client.get('/api/some-endpoint', token=token)
    return render_template('pages/example.html', data=data)
```
**Methods:**
- `api_client.get(endpoint, token=None, params=None)`
- `api_client.post(endpoint, data, token=None)`
- `api_client.put(endpoint, data, token=None)`
- `api_client.patch(endpoint, data, token=None)`
- `api_client.delete(endpoint, token=None)`

**Features:**
- Automatically reads auth token from request context (cookies/headers)
- Accepts optional explicit token parameter
- Constructs full API URL from `API_URL` environment variable

### Client-Side API Helper (JavaScript)

**Location:** `static/js/api_helper.js`

**Purpose:** Used by Alpine.js components for dynamic interactions without page reloads.

**Usage:**
```
javascript
// In Alpine component
async loadData() {
    try {
        const data = await api.get('/api/some-endpoint');
        this.items = data;
    } catch (err) {
        this.error = err.message;
    }
}
```
**Global Object:** `api`

**Methods:**
- `api.get(endpoint, params=null)`
- `api.post(endpoint, data={})`
- `api.put(endpoint, data={})`
- `api.patch(endpoint, data={})`
- `api.delete(endpoint)`

**Features:**
- Automatically reads auth token from cookies
- Automatically adds Authorization header
- Handles 401 responses (redirects to login)
- Handles 204 No Content responses
- Throws errors with messages for easy catch handling
- Uses `window.API_URL` for base URL

### API URL Configuration

The API URL is configured via environment variable and made available to both server and client:

**Server-side:**
```
python
# In webapp.py
API_URL = os.getenv('API_URL')

# Made available to templates via context processor
@app.context_processor
def inject_globals():
    return {
        'API_URL': API_URL
    }
```
**Client-side:**
```
html
<!-- In base.html -->
<script>
    window.API_URL = "{{ API_URL }}";
</script>
```
The `api_helper.js` reads from `window.API_URL` automatically.

## Authentication

### Two-Layer Security Model

**Layer 1 - Webapp (UX):**
- Simple cookie presence check (could potentially be spoofed, but would be rejected by the API)
- Uses `@require_auth` decorator from `services/auth.py`
- Redirects to login if no token found


**Layer 2 - API (Real Security):**
- JWT token validation (cryptographic)
- Checks expiration, signature, blacklist

### Auth Utilities

**Location:** `services/auth.py`

**Functions:**
- `get_auth_token()` - Retrieves JWT token from cookies or headers
- `@require_auth` - Decorator to protect routes (redirects to login if no token)

**Usage:**
```
python
from src.webapp.services.auth import require_auth, get_auth_token

@some_bp.route('/protected')
@require_auth
def protected_page():
    token = get_auth_token()
    # ... use token for API calls
```
## Route Blueprints

### Blueprint Structure

Each feature area has its own blueprint in a subdirectory:

    routes/
    └── feature_name/
        ├── __init__.py              # Blueprint registration
        └── feature_handlers.py      # Route handler functions

### Creating a New Blueprint

**Step 1: Create the blueprint directory and files**

`routes/my_feature/__init__.py`:
```
python
from flask import Blueprint

my_feature_bp = Blueprint('my_feature', __name__, url_prefix='/my-feature')

from . import my_feature_handlers
```
`routes/my_feature/my_feature_handlers.py`:
```
python
from flask import render_template
from . import my_feature_bp
from src.webapp.services.auth import require_auth

@my_feature_bp.route('/')
@require_auth
def index():
    return render_template('pages/my_feature/index.html')
```
**Step 2: Register the blueprint in `webapp.py`:**
```
python
from src.webapp.routes.my_feature import my_feature_bp

app.register_blueprint(my_feature_bp)
```
**Step 3: Create the template directory and file**
- Create directory: `templates/pages/my_feature/`
- Create template: `templates/pages/my_feature/index.html`

### URL Construction

With a blueprint named `my_feature_bp` and `url_prefix='/my-feature'`:
- Route `@my_feature_bp.route('/')` → URL `/my-feature/`
- Route `@my_feature_bp.route('/detail')` → URL `/my-feature/detail`

In templates, reference with blueprint name:
```
python
url_for('my_feature.index')        # /my-feature/
url_for('my_feature.detail')       # /my-feature/detail
```
## Templates

### Template Structure

**base.html:**
- Root template with HTML structure
- Includes Bulma CSS, Alpine.js, Font Awesome
- Defines navbar via `{% include 'components/navbar.html' %}`
- Defines blocks: `title`, `styles`, `content`, `scripts`

**components/:**
- Reusable UI fragments
- Included via `{% include 'components/navbar.html' %}`
- Can be parameterized using Jinja macros if needed

**pages/:**
- Full page templates organized in subdirectories by feature
- Each feature gets its own subdirectory (e.g., `pages/auth/`, `pages/component_demo/`)
- General pages (landing, dashboard) can live at the root of `pages/`
- Extend base.html via `{% extends "base.html" %}`
- Override blocks as needed

### Template Organization Pattern

Templates should mirror the route blueprint structure:

    routes/auth/          →  templates/pages/auth/
    routes/demo/          →  templates/pages/component_demo/
    routes/home/          →  templates/pages/ (landing.html, dashboard.html)

### Creating a New Page
```
html
{% extends "base.html" %}

{% block title %}My Page{% endblock %}

{% block content %}
<section class="section">
    <div class="container">
        <h1 class="title">My Page</h1>
        <!-- Page content here -->
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
    // Page-specific Alpine components
    function myComponent() {
        return {
            // component data and methods
        };
    }
</script>
{% endblock %}
```
**Template paths in render_template():**
```
python
render_template('pages/auth/login.html')
render_template('pages/component_demo/component_demo.html')
render_template('pages/dashboard.html')
```
## Alpine.js Patterns

### Basic Component Structure
```
html
<div x-data="myComponent()" x-init="init()">
    <p x-text="message"></p>
    <button @click="doSomething">Click Me</button>
</div>

<script>
function myComponent() {
    return {
        message: 'Hello',
        
        async init() {
            // Load data on component mount
            await this.loadData();
        },
        
        async loadData() {
            try {
                const data = await api.get('/api/endpoint');
                this.message = data.message;
            } catch (err) {
                console.error('Error:', err);
            }
        },
        
        doSomething() {
            this.message = 'Clicked!';
        }
    };
}
</script>
```
### Common Patterns

**Loading States:**
```
html
<button :class="{ 'is-loading': loading }" @click="submit">
    Submit
</button>
```
**Conditional Rendering:**
```
html
<template x-if="showForm">
    <form>...</form>
</template>

<div x-show="error" class="notification is-danger">
    <span x-text="error"></span>
</div>
```
**Form Binding:**
```
html
<input type="text" x-model="formData.username">
```
**API Calls:**
```
javascript
// GET
const data = await api.get('/api/endpoint', { param: 'value' });

// POST
const result = await api.post('/api/endpoint', { field: 'value' });

// PATCH
const updated = await api.patch('/api/endpoint/123', { field: 'new value' });

// DELETE
await api.delete('/api/endpoint/123');
```
## Bulma CSS Patterns

### Layout

**Container:**
```
html
<div class="container">
    <!-- Content constrained to readable width -->
</div>
```
**Columns:**
```
html
<div class="columns">
    <div class="column is-half">Half width</div>
    <div class="column is-half">Half width</div>
</div>
```
**Section:**
```
html
<section class="section">
    <!-- Adds consistent padding -->
</section>
```
### Components

**Box:**
```
html
<div class="box">
    <!-- Card-like container with shadow -->
</div>
```
**Buttons:**
```
html
<button class="button is-primary">Primary</button>
<button class="button is-danger">Danger</button>
<button class="button is-loading">Loading...</button>
```
**Forms:**
```
html
<div class="field">
    <label class="label">Label</label>
    <div class="control has-icons-left">
        <input class="input" type="text">
        <span class="icon is-small is-left">
            <i class="fas fa-user"></i>
        </span>
    </div>
    <p class="help">Help text</p>
</div>
```
**Notifications:**
```
html
<div class="notification is-success">
    Success message
</div>
<div class="notification is-danger">
    Error message
</div>
```
## Common Tasks

### Adding a New Page

1. Create route blueprint in `routes/feature_name/`
2. Register blueprint in `webapp.py`
3. Create page template directory in `templates/pages/feature_name/`
4. Create template file in that directory
5. Add Alpine component in page's `scripts` block if needed
6. Use `api` helper for API calls from client-side

### Adding a Reusable Component

1. Create component file in `templates/components/` (organized by feature if appropriate)
2. Create a demo page in `templates/pages/component_demo/` for testing
3. Add demo route handler in `routes/demo/component_demo_handlers.py`
4. Include component in pages with `{% include 'components/name.html' %}`
5. For parameterized components, use Jinja macros

### Protecting a Route
```
python
from src.webapp.services.auth import require_auth

@my_bp.route('/protected')
@require_auth
def protected_page():
    return render_template('pages/my_feature/protected.html')
```
### Making an API Call

**Server-side (before rendering):**

```python
from src.webapp.services.api_client import api_client
from src.webapp.services.auth import get_auth_token

token = get_auth_token()
data = api_client.get('/api/endpoint', token=token)
```
```


**Client-side (dynamic interaction):**

```
// In Alpine component
const data = await api.get('/api/endpoint');
```


## Development vs Production

### Environment-Specific Features

The component demo blueprint is only registered in non-production environments:

```python
# In webapp.py
if os.getenv('FLASK_ENV') != 'production':
    app.register_blueprint(demo_bp)
```


**Environment Detection:**
- Local: `FLASK_ENV` not set or set to `development`
- Staging: `FLASK_ENV=staging`
- Production: `FLASK_ENV=production`

## Best Practices

### DO

- ✅ Use `@require_auth` for protected pages
- ✅ Use the `api` helper for all client-side API calls
- ✅ Wrap API calls in try/catch and show user-friendly errors
- ✅ Show loading indicators during async operations
- ✅ Extract common HTML patterns into components
- ✅ Create demo pages for all reusable components
- ✅ Use descriptive names for blueprints, handlers, and Alpine components
- ✅ Mirror route structure in `templates/pages/` subdirectories
- ✅ Test components in isolation via demo pages

### DON'T

- ❌ Make API calls directly from templates (use route handlers or Alpine components)
- ❌ Trust client-side auth alone (API validates everything)
- ❌ Skip error handling on API calls
- ❌ Duplicate component logic (extract to reusable components)
- ❌ Build full features before testing components
- ❌ Forget to register blueprints in `webapp.py`
- ❌ Use absolute URLs (use `url_for()` in templates)

## Running the Webapp

### Local Development

    python3 src/webapp/webapp.py

Runs on `http://localhost:5000` with debug mode enabled.

**Prerequisites:**
- API service running on port 5001
- `API_URL` environment variable set (defaults to `http://localhost:5001`)

### Production Deployment

For production deployment instructions, see `infrastructure/README.md`.

## Configuration

### Environment Variables

**Required:**
- `API_URL` - URL of the API service (default: `http://localhost:5001`)

**Optional:**
- `FLASK_ENV` - Environment name (`development`, `staging`, `production`)
- `SECRET_KEY` - Flask secret key for session management



## Further Reading

For detailed implementation examples, refer to:
- `routes/demo/` - Component demo routes and handlers
- `templates/components/tasks/` - Complete set of task-related components
- `templates/pages/component_demo/` - Component demo pages
- `static/js/api_helper.js` - Client-side API utilities
- `services/api_client.py` - Server-side API client

