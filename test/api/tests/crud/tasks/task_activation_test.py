import pytest
import allure


@allure.feature('Tasks')
@allure.story('State Management - Activation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_task_sets_active_true(auth_client):
    """Activate task sets active=true"""
    with allure.step("Create inactive task"):
        created = auth_client.post('/api/tasks', {
            "title": "Inactive task",
            "active": False
        })
        task_id = created['id']
        assert created['active'] is False

    with allure.step("Activate the task"):
        activated = auth_client.patch(f'/api/tasks/{task_id}/activate')

    with allure.step("Verify active is now true"):
        assert activated['id'] == task_id
        assert activated['active'] is True
        assert activated['title'] == created['title']


@allure.feature('Tasks')
@allure.story('State Management - Activation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_already_active_task(auth_client):
    """Activate already active task is idempotent"""
    with allure.step("Create active task"):
        created = auth_client.post('/api/tasks', {
            "title": "Already active task"
        })
        task_id = created['id']
        assert created['active'] is True

    with allure.step("Activate the task again"):
        activated = auth_client.patch(f'/api/tasks/{task_id}/activate')

    with allure.step("Verify task remains active with no error"):
        assert activated['id'] == task_id
        assert activated['active'] is True


@allure.feature('Tasks')
@allure.story('State Management - Activation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_nonexistent_task(auth_client):
    """Activate nonexistent task returns 404"""
    with allure.step("Attempt to activate task with invalid ID"):
        response = auth_client.patch('/api/tasks/999999/activate',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('State Management - Activation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_another_users_task(auth_client, secondary_auth_client):
    """Activate another user's task returns 404"""
    with allure.step("Create task as first user"):
        user1_task = auth_client.post('/api/tasks', {
            "title": "User 1 task",
            "active": False
        })
        user1_task_id = user1_task['id']

    with allure.step("Attempt to activate first user's task as second user"):
        response = secondary_auth_client.patch(
            f'/api/tasks/{user1_task_id}/activate',
            handle_response=False
        )

    with allure.step("Verify 404 response (security through obscurity)"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('State Management - Deactivation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_task_sets_active_false(auth_client):
    """Deactivate task sets active=false"""
    with allure.step("Create active task"):
        created = auth_client.post('/api/tasks', {
            "title": "Active task"
        })
        task_id = created['id']
        assert created['active'] is True

    with allure.step("Deactivate the task"):
        deactivated = auth_client.patch(f'/api/tasks/{task_id}/deactivate')

    with allure.step("Verify active is now false"):
        assert deactivated['id'] == task_id
        assert deactivated['active'] is False
        assert deactivated['title'] == created['title']


@allure.feature('Tasks')
@allure.story('State Management - Deactivation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_already_inactive_task(auth_client):
    """Deactivate already inactive task is idempotent"""
    with allure.step("Create inactive task"):
        created = auth_client.post('/api/tasks', {
            "title": "Already inactive task",
            "active": False
        })
        task_id = created['id']
        assert created['active'] is False

    with allure.step("Deactivate the task again"):
        deactivated = auth_client.patch(f'/api/tasks/{task_id}/deactivate')

    with allure.step("Verify task remains inactive with no error"):
        assert deactivated['id'] == task_id
        assert deactivated['active'] is False


@allure.feature('Tasks')
@allure.story('State Management - Deactivation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_nonexistent_task(auth_client):
    """Deactivate nonexistent task returns 404"""
    with allure.step("Attempt to deactivate task with invalid ID"):
        response = auth_client.patch('/api/tasks/999999/deactivate',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('State Management - Deactivation')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_another_users_task(auth_client, secondary_auth_client):
    """Deactivate another user's task returns 404"""
    with allure.step("Create task as first user"):
        user1_task = auth_client.post('/api/tasks', {
            "title": "User 1 task"
        })
        user1_task_id = user1_task['id']

    with allure.step("Attempt to deactivate first user's task as second user"):
        response = secondary_auth_client.patch(
            f'/api/tasks/{user1_task_id}/deactivate',
            handle_response=False
        )

    with allure.step("Verify 404 response (security through obscurity)"):
        assert response.status_code == 404