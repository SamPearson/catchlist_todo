import pytest
import allure


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_open(auth_client):
    """Change status to open"""
    with allure.step("Create project with waiting status"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']
        auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "waiting"
        })

    with allure.step("Change status to open"):
        updated = auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "open"
        })

    with allure.step("Verify status is open"):
        assert updated['status'] == "open"


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_waiting(auth_client):
    """Change status to waiting"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']

    with allure.step("Change status to waiting"):
        updated = auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "waiting"
        })

    with allure.step("Verify status is waiting"):
        assert updated['status'] == "waiting"


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_deferred(auth_client):
    """Change status to deferred"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']

    with allure.step("Change status to deferred"):
        updated = auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "deferred"
        })

    with allure.step("Verify status is deferred"):
        assert updated['status'] == "deferred"


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_declined(auth_client):
    """Change status to declined"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']

    with allure.step("Change status to declined"):
        updated = auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "declined"
        })

    with allure.step("Verify status is declined"):
        assert updated['status'] == "declined"


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_stale(auth_client):
    """Change status to stale"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']

    with allure.step("Change status to stale"):
        updated = auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "stale"
        })

    with allure.step("Verify status is stale"):
        assert updated['status'] == "stale"


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_invalid_value(auth_client):
    """Change status to invalid value returns 400 error"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']

    with allure.step("Attempt to change status to invalid value"):
        response = auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "invalid_status"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_without_status_field(auth_client):
    """Change status without status field returns 400 error"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']

    with allure.step("Attempt to change status without status field"):
        response = auth_client.patch(f'/api/projects/{project_id}/status', {},
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_with_empty_request_body(auth_client):
    """Change status with empty request body returns 400 error"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to change status"
        })
        project_id = project['id']

    with allure.step("Attempt to change status with empty body"):
        response = auth_client.patch(f'/api/projects/{project_id}/status', {},
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_on_nonexistent_project(auth_client):
    """Change status on nonexistent project returns 404"""
    with allure.step("Attempt to change status on nonexistent project"):
        response = auth_client.patch('/api/projects/999999/status', {
            "status": "waiting"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Change Status')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_on_another_users_project(auth_client, secondary_auth_client):
    """Change status on another user's project returns 404"""
    with allure.step("Create project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        project_id = project['id']

    with allure.step("Attempt to change status as first user"):
        response = auth_client.patch(f'/api/projects/{project_id}/status', {
            "status": "waiting"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify project status unchanged for second user"):
        get_response = secondary_auth_client.get(f'/api/projects/{project_id}')
        assert get_response['status'] == "open"