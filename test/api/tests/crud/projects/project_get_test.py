import pytest
import allure


@allure.feature('Projects')
@allure.story('Get Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_project_returns_full_object(auth_client):
    """Get project returns complete object with all fields"""
    with allure.step("Create project with multiple fields"):
        created = auth_client.post('/api/projects', {
            "title": "Full project",
            "description": "Test description",
            "win_condition": "All done",
            "reason": "Important",
            "next_step": "Start working"
        })
        project_id = created['id']

    with allure.step("Retrieve the project"):
        retrieved = auth_client.get(f'/api/projects/{project_id}')

    with allure.step("Verify all fields are present"):
        assert retrieved['id'] == project_id
        assert retrieved['title'] == "Full project"
        assert retrieved['description'] == "Test description"
        assert retrieved['win_condition'] == "All done"
        assert retrieved['reason'] == "Important"
        assert retrieved['next_step'] == "Start working"
        assert 'completed' in retrieved
        assert 'completed_at' in retrieved
        assert 'active' in retrieved
        assert 'status' in retrieved
        assert 'created_at' in retrieved
        assert 'updated_at' in retrieved
        assert 'tags' in retrieved
        assert 'principles' in retrieved


@allure.feature('Projects')
@allure.story('Get Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_project(auth_client):
    """Get nonexistent project returns 404"""
    with allure.step("Attempt to get project with invalid ID"):
        response = auth_client.get('/api/projects/999999', handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Get Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_project(auth_client, secondary_auth_client):
    """Get another user's project returns 404 (not 403)"""
    with allure.step("Create project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        project_id = project['id']

    with allure.step("Attempt to get project as first user"):
        response = auth_client.get(f'/api/projects/{project_id}', handle_response=False)

    with allure.step("Verify 404 response (acts as if doesn't exist)"):
        assert response.status_code == 404