import pytest
import allure


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_title(auth_client):
    """Update task title and verify change persists"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {
            "title": "Original title",
            "description": "Original description"
        })
        task_id = created['id']

    with allure.step("Update task title"):
        updated = auth_client.put(f'/api/tasks/{task_id}', {
            "title": "Updated title"
        })

    with allure.step("Verify title changed"):
        assert updated['title'] == "Updated title"
        assert updated['id'] == task_id

    with allure.step("Verify change persists on retrieval"):
        retrieved = auth_client.get(f'/api/tasks/{task_id}')
        assert retrieved['title'] == "Updated title"


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_description(auth_client):
    """Update task description and verify change persists"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {
            "title": "Test task",
            "description": "Original description"
        })
        task_id = created['id']

    with allure.step("Update task description"):
        updated = auth_client.put(f'/api/tasks/{task_id}', {
            "description": "Updated description"
        })

    with allure.step("Verify description changed"):
        assert updated['description'] == "Updated description"
        assert updated['id'] == task_id

    with allure.step("Verify change persists on retrieval"):
        retrieved = auth_client.get(f'/api/tasks/{task_id}')
        assert retrieved['description'] == "Updated description"


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_title_and_description_together(auth_client):
    """Update both title and description in single request"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {
            "title": "Original title",
            "description": "Original description"
        })
        task_id = created['id']

    with allure.step("Update both title and description"):
        updated = auth_client.put(f'/api/tasks/{task_id}', {
            "title": "New title",
            "description": "New description"
        })

    with allure.step("Verify both fields changed"):
        assert updated['title'] == "New title"
        assert updated['description'] == "New description"
        assert updated['id'] == task_id


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_with_empty_title(auth_client):
    """Update task with empty title returns 400"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {
            "title": "Original title"
        })
        task_id = created['id']

    with allure.step("Attempt to update with empty title"):
        response = auth_client.put(f'/api/tasks/{task_id}', {
            "title": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_with_no_data(auth_client):
    """Update task with no data returns 400"""
    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.put(f'/api/tasks/{task_id}', {}, 
                                    handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_with_disallowed_field_status(auth_client):
    """Update task with disallowed field 'status' returns 400"""
    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Attempt to update status via PUT endpoint"):
        response = auth_client.put(f'/api/tasks/{task_id}', {
            "status": "waiting"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_with_disallowed_field_active(auth_client):
    """Update task with disallowed field 'active' returns 400"""
    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Attempt to update active via PUT endpoint"):
        response = auth_client.put(f'/api/tasks/{task_id}', {
            "active": False
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_with_disallowed_field_completed(auth_client):
    """Update task with disallowed field 'completed' returns 400"""
    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Attempt to update completed via PUT endpoint"):
        response = auth_client.put(f'/api/tasks/{task_id}', {
            "completed": True
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_with_disallowed_field_completed_at(auth_client):
    """Update task with disallowed field 'completed_at' returns 400"""
    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Attempt to update completed_at via PUT endpoint"):
        response = auth_client.put(f'/api/tasks/{task_id}', {
            "completed_at": "2025-01-01T00:00:00Z"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_task_with_disallowed_field_project_id(auth_client):
    """Update task with disallowed field 'project_id' returns 400"""
    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Attempt to update project_id via PUT endpoint"):
        response = auth_client.put(f'/api/tasks/{task_id}', {
            "project_id": 123
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_task(auth_client):
    """Update nonexistent task returns 404"""
    with allure.step("Attempt to update nonexistent task"):
        response = auth_client.put('/api/tasks/999999', {
            "title": "Updated title"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Update Task')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_users_task(auth_client, secondary_auth_client):
    """Update another user's task returns 404"""
    with allure.step("Create task as first user"):
        task = auth_client.post('/api/tasks', {
            "title": "User 1 task"
        })
        task_id = task['id']

    with allure.step("Attempt to update first user's task as second user"):
        response = secondary_auth_client.put(f'/api/tasks/{task_id}', {
            "title": "Hacked title"
        }, handle_response=False)

    with allure.step("Verify 404 response (security through obscurity)"):
        assert response.status_code == 404