import pytest
import allure


@allure.feature('Projects')
@allure.story('Delete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_project_returns_204(auth_client):
    """Delete project returns 204 No Content"""
    with allure.step("Create project to delete"):
        created = auth_client.post('/api/projects', {
            "title": "Project to delete"
        })
        project_id = created['id']

    with allure.step("Delete project"):
        response = auth_client.delete(f'/api/projects/{project_id}',
                                      handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204


@allure.feature('Projects')
@allure.story('Delete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_project_actually_removes_it(auth_client):
    """Delete project actually removes it from database"""
    with allure.step("Create project to delete"):
        created = auth_client.post('/api/projects', {
            "title": "Project to delete"
        })
        project_id = created['id']

    with allure.step("Delete project"):
        auth_client.delete(f'/api/projects/{project_id}',
                          handle_response=False)

    with allure.step("Verify project is gone (GET returns 404)"):
        get_response = auth_client.get(f'/api/projects/{project_id}',
                                       handle_response=False)
        assert get_response.status_code == 404


@allure.feature('Projects')
@allure.story('Delete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_project_with_subtasks_cascade(auth_client):
    """Delete project with subtasks deletes all subtasks (cascade)"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project with subtasks"
        })
        project_id = project['id']

    with allure.step("Create 2 subtasks"):
        task1 = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Subtask 1"
        })
        task2 = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Subtask 2"
        })
        task1_id = task1['id']
        task2_id = task2['id']

    with allure.step("Delete project"):
        auth_client.delete(f'/api/projects/{project_id}',
                          handle_response=False)

    with allure.step("Verify project is deleted"):
        project_response = auth_client.get(f'/api/projects/{project_id}',
                                           handle_response=False)
        assert project_response.status_code == 404

    with allure.step("Verify subtasks are also deleted"):
        task1_response = auth_client.get(f'/api/tasks/{task1_id}',
                                         handle_response=False)
        task2_response = auth_client.get(f'/api/tasks/{task2_id}',
                                         handle_response=False)
        assert task1_response.status_code == 404
        assert task2_response.status_code == 404


@allure.feature('Projects')
@allure.story('Delete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_project(auth_client):
    """Delete nonexistent project returns 404"""
    with allure.step("Attempt to delete nonexistent project"):
        response = auth_client.delete('/api/projects/999999',
                                      handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Delete Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.delete
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_users_project(auth_client, secondary_auth_client):
    """Delete another user's project returns 404"""
    with allure.step("Create project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        project_id = project['id']

    with allure.step("Attempt to delete as first user"):
        response = auth_client.delete(f'/api/projects/{project_id}',
                                      handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify project still exists for second user"):
        get_response = secondary_auth_client.get(f'/api/projects/{project_id}')
        assert get_response['id'] == project_id