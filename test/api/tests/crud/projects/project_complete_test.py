import pytest
import allure


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_project_with_no_subtasks(auth_client):
    """Complete project with no subtasks sets completed=true, completed_at, active=false"""
    with allure.step("Create project without subtasks"):
        project = auth_client.post('/api/projects', {
            "title": "Project with no subtasks"
        })
        project_id = project['id']

    with allure.step("Complete the project"):
        completed = auth_client.patch(f'/api/projects/{project_id}/complete')

    with allure.step("Verify project is completed"):
        assert completed['id'] == project_id
        assert completed['completed'] is True
        assert completed['completed_at'] is not None
        assert completed['active'] is False


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_project_sets_completed_at_timestamp(auth_client):
    """Complete project sets completed_at timestamp and is present and recent"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project for completion"
        })
        project_id = project['id']

    with allure.step("Complete the project"):
        completed = auth_client.patch(f'/api/projects/{project_id}/complete')

    with allure.step("Verify completed_at timestamp is set"):
        assert completed['completed_at'] is not None
        assert isinstance(completed['completed_at'], str)
        # Timestamp should be in ISO format
        assert 'T' in completed['completed_at']


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_project_with_all_subtasks_completed(auth_client):
    """Complete project with all subtasks completed succeeds"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project with completed subtasks"
        })
        project_id = project['id']

    with allure.step("Create and complete 2 subtasks"):
        task1 = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Subtask 1"
        })
        task2 = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Subtask 2"
        })
        auth_client.patch(f'/api/tasks/{task1["id"]}/complete')
        auth_client.patch(f'/api/tasks/{task2["id"]}/complete')

    with allure.step("Complete the project"):
        completed = auth_client.patch(f'/api/projects/{project_id}/complete')

    with allure.step("Verify project is completed"):
        assert completed['completed'] is True
        assert completed['completed_at'] is not None


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_project_with_incomplete_subtasks(auth_client):
    """Complete project with incomplete subtasks returns 400 error"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project with incomplete subtask"
        })
        project_id = project['id']

    with allure.step("Create 1 incomplete subtask"):
        auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Incomplete subtask"
        })

    with allure.step("Attempt to complete project"):
        response = auth_client.patch(f'/api/projects/{project_id}/complete',
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_project_with_mixed_subtasks(auth_client):
    """Complete project with mixed subtasks (1 complete, 1 incomplete) returns 400 error"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project with mixed subtasks"
        })
        project_id = project['id']

    with allure.step("Create 2 subtasks, complete only 1"):
        task1 = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Complete subtask"
        })
        auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Incomplete subtask"
        })
        auth_client.patch(f'/api/tasks/{task1["id"]}/complete')

    with allure.step("Attempt to complete project"):
        response = auth_client.patch(f'/api/projects/{project_id}/complete',
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_already_completed_project(auth_client):
    """Complete already completed project is idempotent (no error, stays completed)"""
    with allure.step("Create and complete project"):
        project = auth_client.post('/api/projects', {
            "title": "Already completed project"
        })
        project_id = project['id']
        first_complete = auth_client.patch(f'/api/projects/{project_id}/complete')
        first_completed_at = first_complete['completed_at']

    with allure.step("Complete the project again"):
        second_complete = auth_client.patch(f'/api/projects/{project_id}/complete')

    with allure.step("Verify project remains completed"):
        assert second_complete['completed'] is True
        assert second_complete['completed_at'] == first_completed_at


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_nonexistent_project(auth_client):
    """Complete nonexistent project returns 404"""
    with allure.step("Attempt to complete nonexistent project"):
        response = auth_client.patch('/api/projects/999999/complete',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Complete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_complete_another_users_project(auth_client, secondary_auth_client):
    """Complete another user's project returns 404"""
    with allure.step("Create project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        project_id = project['id']

    with allure.step("Attempt to complete as first user"):
        response = auth_client.patch(f'/api/projects/{project_id}/complete',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify project still incomplete for second user"):
        get_response = secondary_auth_client.get(f'/api/projects/{project_id}')
        assert get_response['completed'] is False


@allure.feature('Projects')
@allure.story('Uncomplete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_project_sets_completed_false(auth_client):
    """Uncomplete project sets completed=false"""
    with allure.step("Create and complete project"):
        project = auth_client.post('/api/projects', {
            "title": "Completed project"
        })
        project_id = project['id']
        auth_client.patch(f'/api/projects/{project_id}/complete')

    with allure.step("Uncomplete the project"):
        uncompleted = auth_client.patch(f'/api/projects/{project_id}/uncomplete')

    with allure.step("Verify completed is false"):
        assert uncompleted['completed'] is False


@allure.feature('Projects')
@allure.story('Uncomplete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_project_clears_completed_at(auth_client):
    """Uncomplete project clears completed_at timestamp"""
    with allure.step("Create and complete project"):
        project = auth_client.post('/api/projects', {
            "title": "Completed project"
        })
        project_id = project['id']
        completed = auth_client.patch(f'/api/projects/{project_id}/complete')
        assert completed['completed_at'] is not None

    with allure.step("Uncomplete the project"):
        uncompleted = auth_client.patch(f'/api/projects/{project_id}/uncomplete')

    with allure.step("Verify completed_at is null"):
        assert uncompleted['completed_at'] is None


@allure.feature('Projects')
@allure.story('Uncomplete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_project_does_not_auto_activate(auth_client):
    """Uncomplete project does NOT auto-activate (active remains false after uncomplete)"""
    with allure.step("Create and complete project"):
        project = auth_client.post('/api/projects', {
            "title": "Completed project"
        })
        project_id = project['id']
        completed = auth_client.patch(f'/api/projects/{project_id}/complete')
        # Verify completion sets active to false
        assert completed['active'] is False

    with allure.step("Uncomplete the project"):
        uncompleted = auth_client.patch(f'/api/projects/{project_id}/uncomplete')

    with allure.step("Verify active remains false"):
        assert uncompleted['active'] is False
        assert uncompleted['completed'] is False


@allure.feature('Projects')
@allure.story('Uncomplete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_already_incomplete_project(auth_client):
    """Uncomplete already incomplete project is idempotent (no error, stays incomplete)"""
    with allure.step("Create project (incomplete by default)"):
        project = auth_client.post('/api/projects', {
            "title": "Incomplete project"
        })
        project_id = project['id']

    with allure.step("Uncomplete the already-incomplete project"):
        uncompleted = auth_client.patch(f'/api/projects/{project_id}/uncomplete')

    with allure.step("Verify project remains incomplete"):
        assert uncompleted['completed'] is False
        assert uncompleted['completed_at'] is None


@allure.feature('Projects')
@allure.story('Uncomplete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_nonexistent_project(auth_client):
    """Uncomplete nonexistent project returns 404"""
    with allure.step("Attempt to uncomplete nonexistent project"):
        response = auth_client.patch('/api/projects/999999/uncomplete',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Uncomplete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_another_users_project(auth_client, secondary_auth_client):
    """Uncomplete another user's project returns 404"""
    with allure.step("Create and complete project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        project_id = project['id']
        secondary_auth_client.patch(f'/api/projects/{project_id}/complete')

    with allure.step("Attempt to uncomplete as first user"):
        response = auth_client.patch(f'/api/projects/{project_id}/uncomplete',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify project still completed for second user"):
        get_response = secondary_auth_client.get(f'/api/projects/{project_id}')
        assert get_response['completed'] is True