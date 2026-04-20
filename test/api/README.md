# API Test Suite

## Overview

The API test automation framework provides comprehensive validation of all API endpoints. It is built with a focus on **pragmatic coverage**, **maintainability**, and **clear reporting**.

**Key Principle:** Tests validate critical functionality and catch regressions without becoming a maintenance burden. **100% coverage is not the goal** - targeted, intentional tests provide better value than exhaustive permutations.

## Technology Stack

- **pytest** - Test runner and framework
- **requests** - HTTP client (wrapped in custom API client)
- **allure** - Advanced test reporting with steps, attachments, and analytics

## Test Structure

    test/api/
    ├── tests/
    │   ├── conftest.py                      # Shared fixtures and configuration
    │   ├── auth_and_connection/             # Authentication and connectivity tests
    │   │   ├── test_auth.py
    │   │   └── test_heartbeat.py
    │   └── crud/                            # CRUD tests organized by entity
    │       ├── calendars/
    │       │   ├── calendar_smoke_test.py   # Critical path coverage
    │       │   ├── calendar_create_test.py
    │       │   ├── calendar_get_test.py
    │       │   ├── calendar_list_test.py
    │       │   ├── calendar_update_test.py
    │       │   ├── calendar_delete_test.py
    │       │   ├── calendar_activation_status_test.py
    │       │   ├── calendar_caldav_discovery_test.py
    │       │   └── calendar_caldav_sync_test.py
    │       ├── checkins/
    │       │   ├── checkin_smoke_test.py
    │       │   ├── checkin_create_test.py
    │       │   ├── checkin_get_test.py
    │       │   ├── checkin_list_test.py
    │       │   ├── checkin_update_test.py
    │       │   └── checkin_delete_test.py
    │       ├── tasks/
    │       ├── projects/
    │       └── [other entities...]
    ├── pytest.ini                           # Pytest configuration and markers
    ├── requirements.txt                     # Test dependencies
    └── README.md

**Naming Convention:** Test files must end with `_test.py` to be discovered by pytest. Use the pattern `{entity}_{action}_test.py`.

## Test Philosophy

### What We Test

**Priority 1: Critical Path (Smoke Tests)**
- Basic CRUD operations for each entity
- Authentication flows (register, login, logout)
- Smoke test failure should mean an entity is entirely unusable

**Priority 2: Extended Functionality**
- Thorough CRUD testing with various data combinations
- Endpoint URL parameters and query string handling
- Field-specific updates and validations
- Edge cases and boundary conditions
- Cross-entity relationships
- Filtering and search capabilities

**What We Don't Test:**
- Exhaustive permutations of field combinations
- Implementation details that may change
- Third-party library functionality

### Test Coverage Strategy

Tests should be **targeted and intentional**, not exhaustive. When adding new tests, consider:

1. **Does this test validate critical functionality?** If the feature is rarely used or cosmetic, it may not need a test.
2. **Will this test catch real regressions?** Tests should protect against realistic failures, not theoretical ones.
3. **Is this already covered by another test?** Avoid redundant tests that verify the same behavior.
4. **How often will this test need updating?** If it will break with every minor change, reconsider the approach.

**A smaller suite of reliable tests is better than a large suite of unreliable ones.**

## Running Tests

### Setup

Activate the virtual environment:

    source venv/bin/activate

If the virtual environment doesn't exist, create it first:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r test/api/requirements.txt

### Common Test Commands


**Running tests with markers:**
Markers enable efficient testing workflows by running only tests relevant to your changes:

- **Working on task endpoints** → `pytest -m tasks`
- **Changed authentication logic** → `pytest -m auth`
- **Quick sanity check** → `pytest -m smoke_test`
- **Validating project CRUD** → `pytest -m "projects and crud"`
- **Pre-deployment verification** → `pytest -m "smoke_test or auth"`

This approach provides **fast, relevant feedback** without running the entire suite for every change.

See `pytest.ini` for the complete list of registered markers.

**Combine markers (AND logic):**

    pytest -m "tasks and smoke_test"

**Combine markers (OR logic):**

    pytest -m "tasks or projects"

**Run specific test file:**

    pytest test/api/tests/crud/tasks/task_create_test.py

**Run specific test function:**

    pytest test/api/tests/crud/tasks/task_create_test.py::test_create_task

**Run with verbose output:**

    pytest -v


### Environment Selection

Run tests against different environments:

    pytest                    # dev (default)
    pytest --env=dev         # explicitly use dev
    pytest --env=staging     # staging environment
    pytest --env=prod        # production environment

Environment configuration is managed via `.env.*` files in the test/api/config/environments/.env.{environemnt_name}
An unpopulated example file named example_env can be found in the same directory.

### Allure Reports

Generate visual test reports with Allure:

    pytest -m "crud and tasks" --alluredir="./reports/$(date +%Y-%m-%d_%H-%M-%S)"

View the report in a browser:

    allure serve reports/2026-03-15_16-45-34/

**Allure Features:**
- Step-by-step test execution flow
- Full request/response bodies for API calls
- Error diagnostics with stack traces
- Test analytics and trends

**Note:** Reports are generated in the `reports/` directory which is excluded from version control.


## Test Anatomy

All tests follow the **Arrange-Act-Assert** pattern within Allure steps:

```python
@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_task(auth_client):
    """Create task with only required field (title)"""

    with allure.step("Prepare test data"):
        # ARRANGE: Set up test data
        data = {"title": "Test task title"}

    with allure.step("Create new task"):
        # ACT: Perform the action being tested
        response = auth_client.post('/api/tasks', data)

    with allure.step("Verify response structure and values"):
        # ASSERT: Validate the results
        assert response['id']
        assert response['title'] == data['title']
        assert response['completed'] is False
```


**Component Breakdown:**

1. **Allure Decorators** - Organize tests in reports (`@allure.feature`, `@allure.story`)
2. **Pytest Markers** - Enable filtering and categorization
3. **Severity Level** - CRITICAL for smoke tests, NORMAL for extended tests, MINOR for edge cases
4. **Function Signature** - Descriptive name and fixture parameter
5. **Docstring** - Brief description appearing in reports
6. **Allure Steps** - Break test into logical phases for clear execution flow

## Authentication Fixtures

Different fixtures provide different levels of authentication and isolation:

### auth_client (DEFAULT)

**Purpose:** Fresh authenticated client for each test

**Characteristics:**
- New user created per test
- Complete isolation between tests
- User deleted immediately after test
- **When to use:** Most tests - default choice for standard CRUD operations

```python
def test_create_task(auth_client):
    response = auth_client.post('/api/tasks', {"title": "Test"})
```


### session_auth_client

**Purpose:** Persistent authenticated client shared across tests

**Characteristics:**
- Shared session user (`test_user`)
- Data persists across tests in session
- User deleted at session end
- **When to use:** Tests that need to verify accumulated state, performance tests

```python
def test_accumulated_tasks(session_auth_client):
    # Data from previous tests using this fixture will still exist
    tasks = session_auth_client.get('/api/tasks')
```


### secondary_auth_client

**Purpose:** Second authenticated user for multi-user scenarios

**Characteristics:**
- Different user than primary test user (`secondary_user`)
- Separate from other fixtures
- User deleted at session end
- **When to use:** Testing data isolation between users, authorization tests

```python
def test_user_isolation(auth_client, secondary_auth_client):
    # Primary user creates task
    task = auth_client.post('/api/tasks', {"title": "Primary"})

    # Secondary user cannot see it
    secondary_tasks = secondary_auth_client.get('/api/tasks')
    ids = [t['id'] for t in secondary_tasks]
    assert task['id'] not in ids
```


### unauthenticated_client

**Purpose:** Client without authentication

**Characteristics:**
- No authentication state
- No cleanup needed
- **When to use:** Testing authentication requirements, public endpoints

```python
@pytest.mark.auth
def test_tasks_require_authentication(unauthenticated_client):
    response = unauthenticated_client.get('/api/tasks',
                                          handle_response=False)
    assert response.status_code == 401
```


### Fixture Quick Reference

| Fixture                | Authenticated | Scope       | Isolation Level | Use Case                 |
|------------------------|---------------|-------------|-----------------|--------------------------|
| auth_client            | Yes           | Per test    | Complete        | Standard tests (DEFAULT) |
| session_auth_client    | Yes           | Per session | Shared state    | Accumulated state tests  |
| secondary_auth_client  | Yes           | Per session | Separate user   | Multi-user scenarios     |
| unauthenticated_client | No            | Per test    | N/A             | Auth requirement tests   |

## Writing Tests

For detailed information on writing new tests, including:
- Complete test structure patterns
- Working with APIResponse objects
- Error handling patterns
- Multi-user testing scenarios
- Common testing patterns (CRUD, errors, relationships)
- Best practices and conventions

**See:** `docs/wiki/Testing/API/Writing_Tests.txt`

This documentation covers test anatomy, fixture usage, assertion patterns, and step-by-step guides for adding new tests to the suite.


