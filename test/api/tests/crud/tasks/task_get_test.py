import pytest
import allure


@allure.feature('Tasks')
@allure.story('Get Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_task_returns_full_object(auth_client):
    """Get task returns complete task object with all fields"""
    with allure.step("Create task with multiple fields"):
        created = auth_client.post('/api/tasks', {
            "title": "Complete task",
            "description": "Full task description",
            "status": "waiting",
            "active": False
        })
        task_id = created['id']

    with allure.step("Retrieve the task"):
        retrieved = auth_client.get(f'/api/tasks/{task_id}')

    with allure.step("Verify all fields are present and correct"):
        # Identity fields
        assert retrieved['id'] == task_id
        assert isinstance(retrieved['id'], int)

        # Content fields
        assert retrieved['title'] == "Complete task"
        assert retrieved['description'] == "Full task description"
        assert isinstance(retrieved['title'], str)
        assert isinstance(retrieved['description'], str)

        # State fields
        assert retrieved['status'] == "waiting"
        assert retrieved['active'] is False
        assert retrieved['completed'] is False
        assert isinstance(retrieved['status'], str)
        assert isinstance(retrieved['active'], bool)
        assert isinstance(retrieved['completed'], bool)

        # Timestamp fields
        assert retrieved['created_at']
        assert retrieved['updated_at']
        assert retrieved['completed_at'] is None
        assert isinstance(retrieved['created_at'], str)
        assert isinstance(retrieved['updated_at'], str)

        # Relationship fields
        assert retrieved['project_id'] is None
        assert retrieved['tags'] == []
        assert retrieved['principles'] == []
        assert isinstance(retrieved['tags'], list)
        assert isinstance(retrieved['principles'], list)


@allure.feature('Tasks')
@allure.story('Get Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_task(auth_client):
    """Get nonexistent task returns 404"""
    with allure.step("Attempt to retrieve task with invalid ID"):
        response = auth_client.get('/api/tasks/999999', handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Get Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_task(auth_client, secondary_auth_client):
    """Get another user's task returns 404 (acts as if it doesn't exist)"""
    with allure.step("Create task as first user"):
        user1_task = auth_client.post('/api/tasks', {"title": "User 1 task"})
        user1_task_id = user1_task['id']

    with allure.step("Attempt to retrieve first user's task as second user"):
        response = secondary_auth_client.get(f'/api/tasks/{user1_task_id}',
                                          handle_response=False)

    with allure.step("Verify 404 response (not 403 - security through obscurity)"):
        assert response.status_code == 404
        # Note: Returns 404 instead of 403 to avoid leaking information
        # about which task IDs exist in the system