# Webapp Layer

## Overview

The webapp provides a server-side rendered web interface for the productivity management system with client-side interactivity. It communicates with a separate API service for all data operations.

**Technology Stack:**
- **Backend**: Python 3.10.12, Flask
- **Frontend**: Custom CSS design system (`static/css/app.css`), Alpine.js, Font Awesome
- **Architecture**: Server-side rendering with client-side interactivity
- **Authentication**: JWT token authentication via cookies

**Current Status:** The webapp is in active development. The API is feature-complete, and the webapp is built incrementally from reusable UI components (Jinja component templates, Alpine.js behavior, and the shared custom CSS design system).

## Directory Structure

    webapp/
    ├── routes/                      # Route blueprints
    │   ├── auth/                    # Authentication routes
    │   │   ├── __init__.py          # Blueprint registration
    │   │   └── auth_handlers.py    # Route handler functions
    │   ├── home/                    # Home/landing + dashboard routes
    │   │   ├── __init__.py
    │   │   └── home_handlers.py
    │   ├── tasks/                   # Task page routes
    │   ├── sessions/                # Session page routes
    │   ├── reports/                 # Report page routes
    │   ├── tags/                    # Tag manager routes
    │   ├── principles/              # Principle manager routes
    │   ├── projects/                # Project page routes
    │   ├── routines/                # Routine page routes
    │   └── calendars/               # Calendar manager routes
    ├── services/                    # Shared services
    │   ├── api_client.py            # Server-side API client
    │   └── auth.py                  # Auth utilities and decorators
    ├── templates/                   # Jinja2 templates
    │   ├── base.html                # Base layout template
    │   ├── components/              # Reusable UI components
    │   │   ├── navbar.html
    │   │   ├── tasks/               # Task components
    │   │   │   ├── task_card.html
    │   │   │   ├── task_create.html
    │   │   │   ├── task_list.html
    │   │   │   └── task_search.html
    │   │   ├── sessions/            # Session components
    │   │   │   ├── session_display.html
    │   │   │   ├── session_list.html
    │   │   │   └── session_search.html
    │   │   └── reports/             # Report components
    │   │       ├── report_display.html
    │   │       └── report_selector.html
    │   └── pages/                   # Full page templates
    │       ├── auth/                # Authentication pages
    │       │   ├── login.html
    │       │   ├── register.html
    │       │   └── account.html
    │       ├── tasks/               # Task page (task_page.html)
    │       ├── sessions/            # Session page (session_page.html)
    │       ├── reports/             # Report page (report_page.html)
    │       ├── tags/                # Tag manager page (tag_page.html)
    │       ├── principles/          # Principle manager page (principle_page.html)
    │       ├── projects/            # Project page (project_page.html)
    │       ├── routines/            # Routine page (routine_page.html)
    │       ├── calendars/           # Calendar manager page (calendar_page.html)
    │       ├── landing.html         # Landing page
    │       └── dashboard.html       # Main dashboard
    ├── static/                      # Static assets
    │   ├── css/
    │   │   └── app.css              # Custom CSS design system
    │   ├── js/
    │   │   ├── api_helper.js        # Client-side API utilities
    │   │   └── components/          # Alpine.js components (per feature + shared/)
    │   └── images/
    └── webapp.py                    # Main Flask application

## Component-Based Development

The webapp follows a component-based approach where UI elements are built as reusable, self-contained pieces.

### Component Structure

Components live in `templates/components/` organized by feature, with matching Alpine.js logic in `static/js/components/`:

    templates/components/
    ├── navbar.html
    ├── tasks/
    │   ├── task_card.html
    │   ├── task_create.html
    │   ├── task_list.html
    │   └── task_search.html
    ├── sessions/
    │   ├── session_display.html
    │   ├── session_list.html
    │   └── session_search.html
    ├── tags/
    │   ├── tag_create.html
    │   └── tag_list.html
    ├── principles/
    │   ├── principle_create.html
    │   └── principle_list.html
    ├── projects/
    │   ├── project_create.html
    │   ├── project_list.html
    │   └── project_search.html
    ├── routines/
    │   ├── routine_create.html
    │   └── routine_list.html
    ├── calendars/
    │   ├── calendar_create.html
    │   └── calendar_list.html
    ├── shared/
    │   └── tag_principle_picker.html
    └── reports/
        ├── report_display.html
        └── report_selector.html

Each component is:
- **Self-contained**: Includes its own Alpine.js logic, which either lives in the component/paging template or in a matching file under `static/js/components/`
- **Reusable**: Can be included in multiple pages, either directly or via Jinja macros
- **Styleable**: Uses classes from the shared design system in `static/css/app.css`

#### Shared: Tag / Principle Picker

`templates/components/shared/tag_principle_picker.html` defines a macro that attaches/detaches tags and principles to any entity via the Attach/Detach endpoints:

    {% from "components/shared/tag_principle_picker.html" import tag_principle_picker %}
    {{ tag_principle_picker(target_type, target_id_expr, attached_tags_expr, attached_principles_expr, testid) }}

- `target_type`: entity type (`task`, `project`, `routine`, `session`, `calendar`, `report`)
- `target_id_expr` / attached arrays: Alpine expressions evaluated in the enclosing component's scope (e.g. `task.id`, `task.tags`)
- Configure the Alpine root with `x-data="tagPrinciplePicker({...})"`; logic lives in `static/js/components/shared/tag_principle_picker.js`
- Add the script to the page `scripts` block: `<script src="{{ url_for('static', filename='js/components/shared/tag_principle_picker.js') }}"></script>`
- For entities that don't exist yet (e.g. a task during create), wrap the macro in `<template x-if="...">` so the picker initializes only once the entity exists.

Pages compose components inside their own layout shell (`.page-head`, `.container`, etc.). Some components render their own `.box` shell (e.g. the task/session search and create forms); page templates should not re-wrap those in another box. Pages load the component JS they need in their `scripts` block:

    <!-- templates/pages/tasks/task_page.html -->
    ...
    {% block scripts %}
    <script>const INITIAL_TASKS = {{ initial_tasks | tojson }};</script>
    <script src="{{ url_for('static', filename='js/components/tasks/task_card.js') }}"></script>
    <script src="{{ url_for('static', filename='js/components/tasks/task_list.js') }}"></script>
    <script src="{{ url_for('static', filename='js/components/tasks/task_create.js') }}"></script>
    <script src="{{ url_for('static', filename='js/components/tasks/task_search.js') }}"></script>
    {% endblock %}

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
- Includes the custom design system (`static/css/app.css`), Alpine.js, Font Awesome
- Defines navbar via `{% include 'components/navbar.html' %}`
- Defines blocks: `title`, `styles`, `content`, `scripts`

**components/:**
- Reusable UI fragments
- Included via `{% include 'components/navbar.html' %}`
- Can be parameterized using Jinja macros if needed

**pages/:**
- Full page templates organized in subdirectories by feature
- Each feature gets its own subdirectory (e.g., `pages/auth/`, `pages/tasks/`)
- General pages (landing, dashboard) can live at the root of `pages/`
- Extend base.html via `{% extends "base.html" %}`
- Override blocks as needed

### Template Organization Pattern

Templates should mirror the route blueprint structure:

    routes/auth/          →  templates/pages/auth/
    routes/tasks/         →  templates/pages/tasks/
    routes/sessions/      →  templates/pages/sessions/
    routes/reports/       →  templates/pages/reports/
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
render_template('pages/tasks/task_page.html')
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
## Custom CSS Design System

The webapp uses a custom design system defined in `static/css/app.css` — there is no CSS framework. It is built on CSS custom properties (design tokens) with light and dark themes:

```
css
:root { ... }                    /* Light theme tokens */
:root[data-theme='dark'] { ... } /* Dark theme tokens */
```

A small pre-paint script in `base.html` applies the theme by reading a saved preference from `localStorage` (falling back to `prefers-color-scheme`), so there is no flash of the wrong theme.

### Design Tokens

- **Colors**: `--gold`, `--gold-strong`, `--gold-soft`, `--bg`, `--surface`, `--surface-2`, `--hairline`, `--text`, `--muted`, `--success`, `--warning`, `--info`, `--danger`, `--grey`, plus soft variants (`--success-soft`, etc.) and `--hover`, `--field`, `--field-focus-ring`
- **Type**: `--font` (EB Garamond) for body, `--font-display` (Cormorant Garamond) for headings, `--mono` (IBM Plex Mono) for metadata and readouts
- **Misc**: `--radius`, `--shadow-warm` (engraved feel)

### Page Layout

Pages share a `section.section > div.container` shell with a `.page-head` banner:

```
html
<section class="section">
    <div class="container">
        <div class="page-head">
            <h1 class="page-title">Tasks</h1>
            <p class="page-subtitle">Capture and clear your work</p>
        </div>
        <!-- page content: boxes, cards, components -->
    </div>
</section>
```

- `.page-head` — adds a decorative `✦ ❖ ✦` rule beneath the title
- `.page-title` — large display heading (Cormorant, ~40px)
- `.page-subtitle` — muted secondary line

### Boxes & Cards

```
html
<div class="box">
    <div class="box-header">
        <h2 class="box-title"><span class="icon"><i class="fas fa-tasks"></i></span> Section Title</h2>
    </div>
    <div class="box-body">
        <!-- content -->
    </div>
</div>
```

- `.box` / `.box-pad` — primary card container (surface, gold border, warm shadow)
- `.box-header` / `.box-title` / `.box-body` — section framing (optionally collapsible)
- `.card` — used for grids such as the dashboard; variants `.card.live`, `.card.disabled`, plus `.card-icon`, `.card-title`, `.card-desc`
- `.grid` — responsive 3-column grid (collapses to fewer columns on smaller screens); `.grid-2` for two columns

### Buttons

Both `class="button"` and `class="btn"` map to the same base; the legacy `is-*` modifiers are kept as aliases:

```
html
<button class="button is-primary">Primary</button>
<button class="btn btn-ghost">Ghost</button>
<button class="button is-danger">Danger</button>
<button class="button is-success">Success</button>
<button class="button is-warning">Warning</button>
<button class="button is-info">Info</button>
<button class="btn btn-link">Link</button>

<button class="button is-primary is-fullwidth">Block</button>   <!-- also .btn-full -->
<button class="btn btn-sm">Small</button>                        <!-- also .button.is-small -->
```

Use `:class="{ 'is-loading': saving }"` in Alpine components to show a spinner while a request is in flight.

### Forms

```
html
<div class="field">
    <label class="label">Email</label>
    <div class="control has-icons-left">
        <input class="input" type="email">
        <span class="icon is-small"><i class="fas fa-envelope"></i></span>
    </div>
    <p class="help">We'll never share your email.</p>
</div>

<select class="select">...</select>           <!-- styled select -->
<select class="select is-fullwidth">...</select>
```

### Notifications

```
html
<div class="notification is-success">
    <span>&#10003; Saved</span>
    <button class="note-close" @click="show = false">&#10005;</button>
</div>

<div class="notification is-danger">
    <span x-text="error"></span>
</div>
```

Variants: `is-success`, `is-danger`, `is-info`, `is-warning`, `is-light`. Use `.note-close` as the dismiss button (the legacy `.delete` has no visible glyph).

### Feature Components

`app.css` also defines styles for each feature area:

- **Tasks**: `.task-card`, `.task-status-icon`, `.status-open`, `.status-waiting`, `.status-deferred`, `.status-declined`, `.status-stale`, `.task-title`, `.task-badges`, `.task-detail`, `.task-meta`, `.task-actions`, `.empty-state`
- **Sessions**: `.session-card`, `.session-row`, `.session-color`, `.session-title`, `.session-when`, `.session-detail`, `.checkin`, `.rpe`, `.session-list`
- **Reports**: `.tabs`, `.tab`, `.picker-row`, `.report-nav`, `.report-head`, `.report-meta`, `.stats`, `.stat`, `.stat-blue`, `.stat-green`, `.block`, `.block-label`, `.block-input`, `.section-title`, `.chip-row`, `.chip`, `.day-stub`, `.check-row`, `.mini-list`, `.mini-item`, `.mini-empty`
- **Shared**: `.tag` plus `.tag-info/.tag-success/.tag-warning/.tag-danger/.tag-grey/.tag-link`, `.notification`, `.modal`, `.section-title`

### Utilities

Spacing (`mt-*`, `mb-*`, `ml-*`, `mr-*`, `p-*`, `px-*`, `py-*`, etc.), flex helpers (`is-flex`, `is-flex-grow-1`, `is-flex-wrap-wrap`, `is-align-items-*`, `is-justify-content-*`), visibility (`.hidden`), and text/background helpers (`has-text-*`, `has-background-*`, `is-size-1`…`is-size-7`) are available for quick composition.

### Legacy Class Names

For backwards compatibility, a number of legacy class names (`columns`, `column is-*`, `title is-*`, `subtitle`, `section`, `container`, `button is-*`, etc.) still resolve to the design system. **New code should prefer the native classes above.**
## Common Tasks

### Adding a New Page

1. Create route blueprint in `routes/feature_name/`
2. Register blueprint in `webapp.py`
3. Create page template directory in `templates/pages/feature_name/`
4. Create template file in that directory
5. Add Alpine component in page's `scripts` block if needed
6. Use `api` helper for API calls from client-side

### Adding a Reusable Component

1. Create the component markup in `templates/components/` (organized by feature if appropriate)
2. Add its Alpine.js logic in `static/js/components/<feature>/<name>.js` (or inline in the template for small self-contained widgets)
3. Include the component in pages with `{% include 'components/name.html' %}` (or a Jinja macro for parameterized components)
4. Load the matching JS in the page's `scripts` block
5. Use classes from the design system (`static/css/app.css`) for styling; add new styles there if the component needs them

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

### Environment Detection
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
- ✅ Use descriptive names for blueprints, handlers, and Alpine components
- ✅ Mirror route structure in `templates/pages/` subdirectories
- ✅ Add new styles to `static/css/app.css` rather than relying on legacy class names

### DON'T

- ❌ Make API calls directly from templates (use route handlers or Alpine components)
- ❌ Trust client-side auth alone (API validates everything)
- ❌ Skip error handling on API calls
- ❌ Duplicate component logic (extract to reusable components)
- ❌ Wrap a component that renders its own `.box` in another box
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
- `templates/components/` - Reusable component templates (tasks, sessions, reports, navbar)
- `templates/pages/` - Page shells built on the design system
- `static/css/app.css` - The custom design system (tokens, layout, and component styles)
- `static/js/components/` - Alpine.js component logic organized by feature
- `static/js/api_helper.js` - Client-side API utilities
- `services/api_client.py` - Server-side API client

