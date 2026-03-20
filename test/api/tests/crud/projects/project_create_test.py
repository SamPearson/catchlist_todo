import pytest
import allure


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_all_fields(auth_client):
    """Create project with all available fields populated"""
    with allure.step("Create project with all fields"):
        response = auth_client.post('/api/projects', {
            "title": "Complete project with all fields",
            "description": "This project has every field populated",
            "win_condition": "All tasks completed successfully",
            "reason": "This is important work that needs doing",
            "next_step": "Start by creating subtasks",
            "status": "waiting",
            "active": False
        })

    with allure.step("Verify all fields are set correctly"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['title'] == "Complete project with all fields"
        assert response['description'] == "This project has every field populated"
        assert response['win_condition'] == "All tasks completed successfully"
        assert response['reason'] == "This is important work that needs doing"
        assert response['next_step'] == "Start by creating subtasks"
        assert response['status'] == "waiting"
        assert response['active'] is False
        assert response['completed'] is False
        assert response['completed_at'] is None
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_verifies_defaults(auth_client):
    """Create project without optional fields verifies correct defaults"""
    with allure.step("Create project with only title"):
        response = auth_client.post('/api/projects', {
            "title": "Project with defaults"
        })

    with allure.step("Verify default values"):
        assert response['active'] is False, "active should default to false"
        assert response['status'] == "open", "status should default to 'open'"
        assert response['completed'] is False, "completed should default to false"
        assert response['description'] is None, "description should be null when not provided"
        assert response['win_condition'] is None, "win_condition should be null when not provided"
        assert response['reason'] is None, "reason should be null when not provided"
        assert response['next_step'] is None, "next_step should be null when not provided"
        assert response['completed_at'] is None, "completed_at should be null for incomplete project"


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_status_waiting(auth_client):
    """Create project with status 'waiting'"""
    with allure.step("Create project with status=waiting"):
        response = auth_client.post('/api/projects', {
            "title": "Waiting project",
            "status": "waiting"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "waiting"
        assert response['id']


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_status_deferred(auth_client):
    """Create project with status 'deferred'"""
    with allure.step("Create project with status=deferred"):
        response = auth_client.post('/api/projects', {
            "title": "Deferred project",
            "status": "deferred"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "deferred"
        assert response['id']


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_status_declined(auth_client):
    """Create project with status 'declined'"""
    with allure.step("Create project with status=declined"):
        response = auth_client.post('/api/projects', {
            "title": "Declined project",
            "status": "declined"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "declined"
        assert response['id']


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_status_stale(auth_client):
    """Create project with status 'stale'"""
    with allure.step("Create project with status=stale"):
        response = auth_client.post('/api/projects', {
            "title": "Stale project",
            "status": "stale"
        })

    with allure.step("Verify status is set correctly"):
        assert response['status'] == "stale"
        assert response['id']


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_invalid_status(auth_client):
    """Create project with invalid status returns 400"""
    with allure.step("Attempt to create project with invalid status"):
        response = auth_client.post('/api/projects', {
            "title": "Invalid status project",
            "status": "invalid_status"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_without_title(auth_client):
    """Create project without title returns 400"""
    with allure.step("Attempt to create project without title"):
        response = auth_client.post('/api/projects', {
            "description": "Project without title"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_empty_title(auth_client):
    """Create project with empty title returns 400"""
    with allure.step("Attempt to create project with empty title"):
        response = auth_client.post('/api/projects', {
            "title": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_whitespace_only_title(auth_client):
    """Create project with whitespace-only title returns 400"""
    with allure.step("Attempt to create project with whitespace-only title"):
        response = auth_client.post('/api/projects', {
            "title": "   "
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_title_exactly_200_chars(auth_client):
    """Create project with title exactly 200 characters succeeds (boundary test)"""
    with allure.step("Create project with 200-character title"):
        title_200_chars = "A" * 200
        response = auth_client.post('/api/projects', {
            "title": title_200_chars
        })

    with allure.step("Verify project created successfully"):
        assert response['id']
        assert response['title'] == title_200_chars
        assert len(response['title']) == 200


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_title_over_200_chars(auth_client):
    """Create project with title over 200 characters returns 400 (boundary test)"""
    with allure.step("Attempt to create project with 201-character title"):
        title_201_chars = "A" * 201
        response = auth_client.post('/api/projects', {
            "title": title_201_chars
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Create Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_project_with_empty_request_body(auth_client):
    """Create project with empty request body returns 400"""
    with allure.step("Attempt to create project with empty body"):
        response = auth_client.post('/api/projects', {}, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400