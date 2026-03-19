import pytest
import allure


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_all_fields(auth_client):
    """Create task with all available fields populated"""
    with allure.step("Create a project for association"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project",
            "win_condition": "All tasks done",
            "reason": "Testing"
        })
        project_id = project['id']

    with allure.step("Create task with all fields"):
        response = auth_client.post('/api/tasks', {
            "title": "Complete task with all fields",
            "description": "This task has every field populated",
            "status": "waiting",
            "active": False,
            "project_id": project_id
        })

    with allure.step("Verify all fields are set correctly"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['title'] == "Complete task with all fields"
        assert response['description'] == "This task has every field populated"
        assert response['status'] == "waiting"
        assert response['active'] is False
        assert response['project_id'] == project_id
        assert response['completed'] is False
        assert response['completed_at'] is None
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_verifies_defaults(auth_client):
    """Create task without optional fields verifies correct defaults"""
    with allure.step("Create task with only title"):
        response = auth_client.post('/api/tasks', {
            "title": "Task with defaults"
        })

    with allure.step("Verify default values"):
        assert response['active'] is True, "active should default to true"
        assert response['status'] == "open", "status should default to 'open'"
        assert response['completed'] is False, "completed should default to false"
        assert response['description'] is None, "description should be null when not provided"
        assert response['project_id'] is None, "project_id should be null for standalone task"
        assert response['completed_at'] is None, "completed_at should be null for incomplete task"


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_status_waiting(auth_client):
    """Create task with status 'waiting'"""
    with allure.step("Create task with status=waiting"):
        response = auth_client.post('/api/tasks', {
            "title": "Waiting task",
            "status": "waiting"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "waiting"
        assert response['id']


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_status_deferred(auth_client):
    """Create task with status 'deferred'"""
    with allure.step("Create task with status=deferred"):
        response = auth_client.post('/api/tasks', {
            "title": "Deferred task",
            "status": "deferred"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "deferred"
        assert response['id']


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_status_declined(auth_client):
    """Create task with status 'declined'"""
    with allure.step("Create task with status=declined"):
        response = auth_client.post('/api/tasks', {
            "title": "Declined task",
            "status": "declined"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "declined"
        assert response['id']


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_status_stale(auth_client):
    """Create task with status 'stale'"""
    with allure.step("Create task with status=stale"):
        response = auth_client.post('/api/tasks', {
            "title": "Stale task",
            "status": "stale"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "stale"
        assert response['id']


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_active_false(auth_client):
    """Create task with active=false (someday/maybe pile)"""
    with allure.step("Create task with active=false"):
        response = auth_client.post('/api/tasks', {
            "title": "Someday/maybe task",
            "active": False
        })

    with allure.step("Verify active is false"):
        assert response['active'] is False
        assert response['id']


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_invalid_status(auth_client):
    """Create task with invalid status returns 400"""
    with allure.step("Attempt to create task with invalid status"):
        response = auth_client.post('/api/tasks', {
            "title": "Invalid status task",
            "status": "invalid_status"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_without_title(auth_client):
    """Create task without title returns 400"""
    with allure.step("Attempt to create task without title"):
        response = auth_client.post('/api/tasks', {
            "description": "Task without title"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_empty_title(auth_client):
    """Create task with empty title returns 400"""
    with allure.step("Attempt to create task with empty title"):
        response = auth_client.post('/api/tasks', {
            "title": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_whitespace_only_title(auth_client):
    """Create task with whitespace-only title returns 400"""
    with allure.step("Attempt to create task with whitespace-only title"):
        response = auth_client.post('/api/tasks', {
            "title": "   "
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_title_exactly_200_chars(auth_client):
    """Create task with title exactly 200 characters succeeds (boundary test)"""
    with allure.step("Create task with 200-character title"):
        title_200_chars = "A" * 200
        response = auth_client.post('/api/tasks', {
            "title": title_200_chars
        })

    with allure.step("Verify task created successfully"):
        assert response['id']
        assert response['title'] == title_200_chars
        assert len(response['title']) == 200


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_title_over_200_chars(auth_client):
    """Create task with title over 200 characters returns 400 (boundary test)"""
    with allure.step("Attempt to create task with 201-character title"):
        title_201_chars = "A" * 201
        response = auth_client.post('/api/tasks', {
            "title": title_201_chars
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_empty_request_body(auth_client):
    """Create task with empty request body returns 400"""
    with allure.step("Attempt to create task with empty body"):
        response = auth_client.post('/api/tasks', {}, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Create Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_task_with_project_id(auth_client):
    """Create task with project_id makes it a subtask"""
    with allure.step("Create a project"):
        project = auth_client.post('/api/projects', {
            "title": "Parent Project",
            "win_condition": "All subtasks complete",
            "reason": "Testing subtasks"
        })
        project_id = project['id']

    with allure.step("Create task as subtask of project"):
        response = auth_client.post('/api/tasks', {
            "title": "Subtask",
            "project_id": project_id
        })

    with allure.step("Verify task is associated with project"):
        assert response['project_id'] == project_id
        assert response['id']
        assert response['title'] == "Subtask"