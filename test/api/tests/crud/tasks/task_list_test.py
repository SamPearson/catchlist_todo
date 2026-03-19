import pytest
import allure


@allure.feature('Tasks')
@allure.story('List Tasks')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_excludes_completed_by_default(auth_client):
    """List tasks excludes completed tasks by default"""
    with allure.step("Create incomplete and completed tasks"):
        incomplete = auth_client.post('/api/tasks', {"title": "Incomplete task"})
        incomplete_id = incomplete['id']

        completed_task = auth_client.post('/api/tasks', {"title": "Completed task"})
        completed_id = completed_task['id']
        auth_client.patch(f'/api/tasks/{completed_id}/complete')

    with allure.step("List tasks without include_completed parameter"):
        tasks = auth_client.get('/api/tasks')

    with allure.step("Verify only incomplete task is returned"):
        task_ids = [task['id'] for task in tasks]
        assert incomplete_id in task_ids
        assert completed_id not in task_ids


@allure.feature('Tasks')
@allure.story('List Tasks')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_with_include_completed_true(auth_client):
    """List tasks includes completed tasks when include_completed=true"""
    with allure.step("Create incomplete and completed tasks"):
        incomplete = auth_client.post('/api/tasks', {"title": "Incomplete task"})
        incomplete_id = incomplete['id']

        completed_task = auth_client.post('/api/tasks', {"title": "Completed task"})
        completed_id = completed_task['id']
        auth_client.patch(f'/api/tasks/{completed_id}/complete')

    with allure.step("List tasks with include_completed=true"):
        tasks = auth_client.get('/api/tasks', params={'include_completed': 'true'})

    with allure.step("Verify both tasks are returned"):
        task_ids = [task['id'] for task in tasks]
        assert incomplete_id in task_ids
        assert completed_id in task_ids


@allure.feature('Tasks')
@allure.story('List Tasks')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_with_include_completed_false(auth_client):
    """List tasks excludes completed tasks when include_completed=false (explicit)"""
    with allure.step("Create incomplete and completed tasks"):
        incomplete = auth_client.post('/api/tasks', {"title": "Incomplete task"})
        incomplete_id = incomplete['id']

        completed_task = auth_client.post('/api/tasks', {"title": "Completed task"})
        completed_id = completed_task['id']
        auth_client.patch(f'/api/tasks/{completed_id}/complete')

    with allure.step("List tasks with include_completed=false"):
        tasks = auth_client.get('/api/tasks', params={'include_completed': 'false'})

    with allure.step("Verify only incomplete task is returned"):
        task_ids = [task['id'] for task in tasks]
        assert incomplete_id in task_ids
        assert completed_id not in task_ids


@allure.feature('Tasks')
@allure.story('List Tasks')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_returns_empty_array(auth_client):
    """List tasks returns empty array for user with no tasks"""
    with allure.step("List tasks for fresh user"):
        tasks = auth_client.get('/api/tasks')

    with allure.step("Verify empty array is returned"):
        assert isinstance(tasks, list)
        assert len(tasks) == 0


@allure.feature('Tasks')
@allure.story('List Tasks')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_user_isolation(auth_client, secondary_auth_client):
    """List tasks only returns the authenticated user's tasks"""
    with allure.step("Create task for first user"):
        user1_task = auth_client.post('/api/tasks', {"title": "User 1 task"})
        user1_task_id = user1_task['id']

    with allure.step("Create task for second user"):
        user2_task = secondary_auth_client.post('/api/tasks', {"title": "User 2 task"})
        user2_task_id = user2_task['id']

    with allure.step("List tasks for second user"):
        user2_tasks = secondary_auth_client.get('/api/tasks')

    with allure.step("Verify user 2 only sees their own task"):
        task_ids = [task['id'] for task in user2_tasks]
        assert user2_task_id in task_ids
        assert user1_task_id not in task_ids


@allure.feature('Tasks')
@allure.story('List Tasks')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_filters_by_active_status_correctly(auth_client):
    """Verify inactive tasks are handled properly with include_completed param"""
    with allure.step("Create active and inactive tasks"):
        active_task = auth_client.post('/api/tasks', {"title": "Active task"})
        active_id = active_task['id']

        inactive_task = auth_client.post('/api/tasks', {"title": "Inactive task"})
        inactive_id = inactive_task['id']
        auth_client.patch(f'/api/tasks/{inactive_id}/deactivate')

    with allure.step("List all tasks"):
        tasks = auth_client.get('/api/tasks')

    with allure.step("Verify both active and inactive tasks appear"):
        # Note: Based on API docs, the list endpoint filters by completed status,
        # not by active status. Both active and inactive tasks should appear.
        task_ids = [task['id'] for task in tasks]
        assert active_id in task_ids
        assert inactive_id in task_ids

        # Verify active field is correct
        for task in tasks:
            if task['id'] == active_id:
                assert task['active'] is True
            elif task['id'] == inactive_id:
                assert task['active'] is False