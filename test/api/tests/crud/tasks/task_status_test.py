import pytest
import allure


@allure.feature('Tasks')
@allure.story('State Management - Status')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_each_valid_value(auth_client):
    """Change status to each valid value (open, waiting, deferred, declined, stale)"""
    with allure.step("Create task with default status"):
        created = auth_client.post('/api/tasks', {"title": "Test task"})
        task_id = created['id']
        assert created['status'] == "open"

    valid_statuses = ["waiting", "deferred", "declined", "stale", "open"]

    for status in valid_statuses:
        with allure.step(f"Change status to '{status}'"):
            updated = auth_client.patch(f'/api/tasks/{task_id}/status', {
                "status": status
            })

        with allure.step(f"Verify status is now '{status}'"):
            assert updated['id'] == task_id
            assert updated['status'] == status


@allure.feature('Tasks')
@allure.story('State Management - Status')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_to_invalid_value(auth_client):
    """Change status to invalid value returns 400"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {"title": "Test task"})
        task_id = created['id']

    with allure.step("Attempt to change status to invalid value"):
        response = auth_client.patch(f'/api/tasks/{task_id}/status', {
            "status": "invalid_status"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('State Management - Status')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_without_status_field(auth_client):
    """Change status without status field returns 400 with 'status is required' message"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {"title": "Test task"})
        task_id = created['id']

    with allure.step("Attempt to change status with empty request body"):
        response = auth_client.patch(f'/api/tasks/{task_id}/status', {},
                                     handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('State Management - Status')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_with_empty_request_body(auth_client):
    """Change status with empty request body returns 400"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {"title": "Test task"})
        task_id = created['id']

    with allure.step("Attempt to change status with empty request body"):
        response = auth_client.patch(f'/api/tasks/{task_id}/status', {},
                                     handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('State Management - Status')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_on_nonexistent_task(auth_client):
    """Change status on nonexistent task returns 404"""
    with allure.step("Attempt to change status on task with invalid ID"):
        response = auth_client.patch('/api/tasks/999999/status', {
            "status": "waiting"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('State Management - Status')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_change_status_on_another_users_task(auth_client, secondary_auth_client):
    """Change status on another user's task returns 404"""
    with allure.step("Create task as first user"):
        user1_task = auth_client.post('/api/tasks', {"title": "User 1 task"})
        user1_task_id = user1_task['id']

    with allure.step("Attempt to change status on first user's task as second user"):
        response = secondary_auth_client.patch(
            f'/api/tasks/{user1_task_id}/status',
            {"status": "waiting"},
            handle_response=False
        )

    with allure.step("Verify 404 response (security through obscurity)"):
        assert response.status_code == 404