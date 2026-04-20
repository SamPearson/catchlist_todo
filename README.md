# Catchlist

A productivity management system with a focus on clean architecture, separation of concerns, and professional development practices.

## Overview

Catchlist is a full-stack web application for managing tasks, projects, routines, and personal productivity. It demonstrates production-ready patterns including:

- **Clean Architecture**: Three-tier separation (models, repositories, services)
- **API-First Design**: RESTful API backend with separate webapp frontend
- **Component-Based UI**: Reusable UI components with Alpine.js and Bulma CSS
- **Comprehensive Testing**: Automated API test suite with pytest and Allure reporting (selenium testing to follow webapp development)
- **User Authentication**: JWT-based authentication with token blacklisting
- **Data Isolation**: Complete user data separation and ownership enforcement

**Technology Stack:**
- **Backend**: Python 3.10, Flask, SQLAlchemy
- **Frontend**: Bulma CSS, Alpine.js, Jinja2 templates
- **Database**: SQLite via SQLAlchemy ORM
- **Testing**: pytest, Allure, requests, selenium, CI/CD integration
- **Deployment**: Gunicorn, systemd, Nginx, Jenkins CI/CD

## Project Status

- **API Layer**: Feature-complete with comprehensive test coverage
- **Database Layer**: Fully implemented with clean architecture patterns
- **Webapp Layer**: Proof-of-concept phase with component-based development approach
- **Infrastructure**: Production-ready deployment configuration

## Documentation

### Core Architecture

- **[Database Layer](src/database/README.md)** - Models, repositories, services, and architectural patterns
- **[API Layer](src/api/README.md)** - RESTful endpoints, authentication, and request handling
- **[Webapp Layer](src/webapp/README.md)** - Server-side rendering, Alpine.js components, and UI patterns
- **[API Testing](test/api/README.md)** - Test framework, writing tests, and testing philosophy

### Additional Documentation

Comprehensive documentation is available in `docs/wiki/` (Zim wiki format):

- **Entity Design**: `docs/wiki/Design/Entities/` - Purpose-focused entity documentation
- **API Routes**: `docs/wiki/API/Routes/` - Detailed endpoint specifications
- **Testing Guides**: `docs/wiki/Testing/` - Test writing and philosophy

## Quick Start

### Local Development

**1. Clone and setup:**

```bash
git clone <repository-url>
cd catchlist
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
```


**2. Configure environment:**

The api needs a JWT secret key and the webapp needs an API URL.
You can set these environment variables directly in your shell:

```shell script
# Set required environment variables
export JWT_SECRET_KEY="your-secret-key-here"
export API_URL="http://localhost:5001"
```

Or you can set them in `.env` files.

There's an example `.env` file for the jwt key here:
`src/api/config/.env.example`
copy it to .env and populate the JWT_SECRET_KEY variable.

And an example `.env` file for the API URL here:
`src/webapp/config/environments/env.example`
copy it to env.local and populate the API_URL variable.
This variable will only be read from an env file when running the webapp directly instead of through something like gunicorn
See the [infrastructure README](infrastructure/README.md) for more details.




**3. Run both API and webapp:**

```shell script
# Option 1: Use the convenience script (recommended for testing)
python3 run_all.py

# Option 2: Run services individually
# Terminal 1 - API:
python3 -m src.api.api

# Terminal 2 - Webapp:
python3 -m src.webapp.webapp
```


The `run_all.py` script starts both services in parallel and manages their lifecycle. Press Ctrl+C to stop both services.

**4. Access the application:**

- Webapp: `http://localhost:5000`
- API: `http://localhost:5001`

### Running Tests

```shell script
# Access the api test directory
cd test/api/ 
# Activate virtual environment
source venv/bin/activate

# Run all tests (not recommended, there are ~800 tests in total)
pytest

# Run specific test groups
pytest -m smoke_test          # Critical path tests (~60 tests)
pytest -m tasks               # Task-related tests
pytest -m "tasks and crud"    # Task CRUD tests

# Generate Allure report
pytest --alluredir="./reports/$(date +%Y-%m-%d_%H-%M-%S)"
allure serve reports/<timestamp>/

# You can create unique directories for each test run:
pytest --env=dev --alluredir="./reports/test_results`date +%s`" # or however you want to format date

# often on dev, you don't need to view a report twice, so using the same directory is fine
# If I'm going to be running tests repeatedly, I like to keep something like this in my shell:
rm -r reports/oneoff_results && pytest --env=dev --alluredir="./reports/oneoff_results"
# and then to view the results: 
allure serve reports/oneoff_results/
```


See [API Testing Documentation](test/api/README.md) for detailed testing information.

## Project Structure

    catchlist/
    ├── src/
    │   ├── api/                   # RESTful API backend
    │   │   ├── routes/            # API endpoints by entity
    │   │   ├── utils/             # API utilities
    │   │   └── README.md          # API documentation
    │   ├── database/              # Data layer
    │   │   ├── base/              # Base models and repositories
    │   │   ├── tasks/             # Task entity
    │   │   ├── projects/          # Project entity
    │   │   ├── [entities]/        # Additional entities
    │   │   └── README.md          # Database documentation
    │   ├── webapp/                # Web frontend
    │   │   ├── routes/            # Webapp routes
    │   │   ├── templates/         # Jinja2 templates
    │   │   ├── static/            # Static assets
    │   │   └── README.md          # Webapp documentation
    │   └── utils/                 # Shared utilities
    ├── test/
    │   └── api/                   # API test suite
    │       ├── tests/             # Test files
    │       └── README.md          # Testing documentation
    ├── docs/                      # Additional documentation
    │   └── wiki/                  # Zim wiki documentation
    ├── infrastructure/            # Deployment templates
    │   ├── config/                # Environment configs
    │   ├── jenkins_job.sh         # CI/CD job template
    │   ├── sites-available.txt    # Nginx config template
    │   ├── systemd_api.txt        # API service template
    │   └── systemd_webapp.txt     # Webapp service template
    ├── run_all.py                 # Convenience script to run both services
    └── README.md


## Architecture Principles

### Layer Separation

    Webapp (User Interface)
        ↓
    API (HTTP Interface)
        ↓
    Services (Business Logic)
        ↓
    Repositories (Data Access)
        ↓
    Models (Data Structure)

We keep abstraction layers clean by not skipping over any of them;
The webapp doesn't access the database, the api doesn't call repositories directly, etc. 

This prevents us from needing to put all validation and business logic in every layer, etc.

### Data Ownership

All user-scoped data uses `UserOwnedModel` which provides:
- Automatic `user_id` foreign key
- Bidirectional relationships (`entity.user`, `user.entity_list`)
- Cascade deletion (when user is deleted, their data is too)
- Repository-level ownership enforcement (UserOwnedRepository will just 404 if you request something without your user id)

### Security Model

**Webapp Layer (UX):**
- Cookie presence check with `@require_auth` decorator
- Redirects to login if no token found
- Fraudulent cookies could be hacked into a request, but the API layer will reject them when JWT validation fails

**API Layer:**
- JWT token validation (cryptographic)
- Signature verification, expiration check, blacklist check


## Development Workflow

### Adding a New Entity

1. **Database Layer**: Create model, repository, service in `src/database/{entity}/`
2. **API Layer**: Create routes blueprint in `src/api/routes/{entity}/`
3. **Webapp Layer**: Create routes in `src/webapp/routes/{entity}/`, components in `src/webapp/templates/components/{entity}/`, pages in `src/webapp/templates/pages/{entity}/` 
4. **API Tests**: Add test file in `test/api/tests/crud/{entity}/`
5. **Documentation**: Update entity docs in `docs/wiki/Design/Entities/`

See individual layer READMEs for detailed implementation guides.

### Testing Changes

```shell script
# Quick sanity check
pytest -m smoke_test

# Test specific entity
pytest -m tasks

# Test specific functionality
pytest -m "tasks and crud"

# Full test suite
pytest
```


## Deployment

The `infrastructure/` directory contains templates for production deployment:

- **`config/.env.api`** - API environment variables template
- **`jenkins_job.sh`** - CI/CD pipeline template
- **`sites-available.txt`** - Nginx reverse proxy configuration template
- **`systemd_api.txt`** - Systemd service file for API
- **`systemd_webapp.txt`** - Systemd service file for webapp

**Production Stack:**
- Gunicorn (WSGI server)
- Systemd (process management)
- Nginx (reverse proxy)

Copy and customize these templates for your deployment environment.

