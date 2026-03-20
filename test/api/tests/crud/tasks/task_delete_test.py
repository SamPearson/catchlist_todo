import pytest
import allure


@allure.feature('Tasks')
@allure.story('Delete Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_task_returns_204(auth_client):
    """Delete task returns 204 No Content"""
    with allure.step("Create task to delete"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to delete"
        })
        task_id = task['id']

    with allure.step("Delete task"):
        response = auth_client.delete(f'/api/tasks/{task_id}',
                                       handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204


@allure.feature('Tasks')
@allure.story('Delete Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_task_actually_removes_it(auth_client):
    """Delete task actually removes it from the system"""
    with allure.step("Create task to delete"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to delete"
        })
        task_id = task['id']

    with allure.step("Delete task"):
        auth_client.delete(f'/api/tasks/{task_id}', handle_response=False)

    with allure.step("Verify task no longer exists"):
        get_response = auth_client.get(f'/api/tasks/{task_id}',
                                        handle_response=False)
        assert get_response.status_code == 404


@allure.feature('Tasks')
@allure.story('Delete Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_task(auth_client):
    """Delete nonexistent task returns 404"""
    with allure.step("Attempt to delete nonexistent task"):
        response = auth_client.delete('/api/tasks/999999',
                                       handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Delete Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_users_task(auth_client, secondary_auth_client):
    """Delete another user's task returns 404"""
    with allure.step("Create task as first user"):
        task = auth_client.post('/api/tasks', {
            "title": "User 1 task"
        })
        task_id = task['id']

    with allure.step("Attempt to delete first user's task as second user"):
        response = secondary_auth_client.delete(f'/api/tasks/{task_id}',
                                                 handle_response=False)

    with allure.step("Verify 404 response (security through obscurity)"):
        assert response.status_code == 404

    with allure.step("Verify task still exists for original user"):
        retrieved = auth_client.get(f'/api/tasks/{task_id}')
        assert retrieved['id'] == task_id