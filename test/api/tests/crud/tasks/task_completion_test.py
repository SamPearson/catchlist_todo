import pytest
import allure
from datetime import datetime


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_task_sets_completed_true(auth_client):
    """Complete task sets completed=true"""
    with allure.step("Create incomplete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to complete"
        })
        task_id = task['id']
        assert task['completed'] is False

    with allure.step("Complete the task"):
        completed = auth_client.patch(f'/api/tasks/{task_id}/complete')

    with allure.step("Verify completed is true"):
        assert completed['completed'] is True
        assert completed['id'] == task_id


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_task_sets_completed_at_timestamp(auth_client):
    """Complete task sets completed_at timestamp"""
    with allure.step("Create incomplete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to complete"
        })
        task_id = task['id']
        assert task['completed_at'] is None

    with allure.step("Complete the task"):
        completed = auth_client.patch(f'/api/tasks/{task_id}/complete')

    with allure.step("Verify completed_at is set and recent"):
        assert completed['completed_at'] is not None
        assert isinstance(completed['completed_at'], str)

        # Parse timestamp and verify it's recent (within last minute)
        completed_at = datetime.fromisoformat(completed['completed_at'].replace('Z', '+00:00'))
        now = datetime.now(completed_at.tzinfo)
        time_diff = (now - completed_at).total_seconds()
        assert time_diff >= 0, "completed_at should not be in the future"
        assert time_diff < 60, "completed_at should be recent (within last minute)"


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_task_with_toggle_false(auth_client):
    """Complete task with toggle=false always completes (same as no param)"""
    with allure.step("Create incomplete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to complete"
        })
        task_id = task['id']

    with allure.step("Complete task with toggle=false"):
        completed = auth_client.patch(f'/api/tasks/{task_id}/complete?toggle=false')

    with allure.step("Verify task is completed"):
        assert completed['completed'] is True
        assert completed['completed_at'] is not None


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_task_with_toggle_true_on_incomplete_task(auth_client):
    """Complete task with toggle=true on incomplete task completes it"""
    with allure.step("Create incomplete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to complete"
        })
        task_id = task['id']
        assert task['completed'] is False

    with allure.step("Complete task with toggle=true"):
        result = auth_client.patch(f'/api/tasks/{task_id}/complete?toggle=true')

    with allure.step("Verify task is completed"):
        assert result['completed'] is True
        assert result['completed_at'] is not None


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_task_with_toggle_true_on_completed_task(auth_client):
    """Complete task with toggle=true on completed task uncompletes it"""
    with allure.step("Create and complete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to toggle"
        })
        task_id = task['id']
        completed = auth_client.patch(f'/api/tasks/{task_id}/complete')
        assert completed['completed'] is True

    with allure.step("Toggle completion (should uncomplete)"):
        result = auth_client.patch(f'/api/tasks/{task_id}/complete?toggle=true')

    with allure.step("Verify task is uncompleted"):
        assert result['completed'] is False
        assert result['completed_at'] is None


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_already_completed_task(auth_client):
    """Complete already completed task is idempotent"""
    with allure.step("Create and complete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to complete"
        })
        task_id = task['id']
        first_complete = auth_client.patch(f'/api/tasks/{task_id}/complete')
        first_completed_at = first_complete['completed_at']

    with allure.step("Complete task again"):
        second_complete = auth_client.patch(f'/api/tasks/{task_id}/complete')

    with allure.step("Verify task stays completed with same timestamp"):
        assert second_complete['completed'] is True
        assert second_complete['completed_at'] == first_completed_at


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_nonexistent_task(auth_client):
    """Complete nonexistent task returns 404"""
    with allure.step("Attempt to complete nonexistent task"):
        response = auth_client.patch('/api/tasks/999999/complete',
                                      handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Complete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_complete_another_users_task(auth_client, secondary_auth_client):
    """Complete another user's task returns 404"""
    with allure.step("Create task as first user"):
        task = auth_client.post('/api/tasks', {
            "title": "User 1 task"
        })
        task_id = task['id']

    with allure.step("Attempt to complete first user's task as second user"):
        response = secondary_auth_client.patch(f'/api/tasks/{task_id}/complete',
                                                handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify task remains incomplete for original user"):
        retrieved = auth_client.get(f'/api/tasks/{task_id}')
        assert retrieved['completed'] is False


@allure.feature('Tasks')
@allure.story('Uncomplete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_task_sets_completed_false(auth_client):
    """Uncomplete task sets completed=false"""
    with allure.step("Create and complete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to uncomplete"
        })
        task_id = task['id']
        auth_client.patch(f'/api/tasks/{task_id}/complete')

    with allure.step("Uncomplete the task"):
        uncompleted = auth_client.patch(f'/api/tasks/{task_id}/uncomplete')

    with allure.step("Verify completed is false"):
        assert uncompleted['completed'] is False
        assert uncompleted['id'] == task_id


@allure.feature('Tasks')
@allure.story('Uncomplete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_task_clears_completed_at(auth_client):
    """Uncomplete task clears completed_at timestamp"""
    with allure.step("Create and complete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to uncomplete"
        })
        task_id = task['id']
        completed = auth_client.patch(f'/api/tasks/{task_id}/complete')
        assert completed['completed_at'] is not None

    with allure.step("Uncomplete the task"):
        uncompleted = auth_client.patch(f'/api/tasks/{task_id}/uncomplete')

    with allure.step("Verify completed_at is null"):
        assert uncompleted['completed_at'] is None


@allure.feature('Tasks')
@allure.story('Uncomplete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_already_incomplete_task(auth_client):
    """Uncomplete already incomplete task is idempotent"""
    with allure.step("Create incomplete task"):
        task = auth_client.post('/api/tasks', {
            "title": "Already incomplete task"
        })
        task_id = task['id']
        assert task['completed'] is False

    with allure.step("Uncomplete task (already incomplete)"):
        uncompleted = auth_client.patch(f'/api/tasks/{task_id}/uncomplete')

    with allure.step("Verify task stays incomplete"):
        assert uncompleted['completed'] is False
        assert uncompleted['completed_at'] is None


@allure.feature('Tasks')
@allure.story('Uncomplete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_nonexistent_task(auth_client):
    """Uncomplete nonexistent task returns 404"""
    with allure.step("Attempt to uncomplete nonexistent task"):
        response = auth_client.patch('/api/tasks/999999/uncomplete',
                                      handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Uncomplete Task')
@pytest.mark.tasks
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_uncomplete_another_users_task(auth_client, secondary_auth_client):
    """Uncomplete another user's task returns 404"""
    with allure.step("Create and complete task as first user"):
        task = auth_client.post('/api/tasks', {
            "title": "User 1 task"
        })
        task_id = task['id']
        auth_client.patch(f'/api/tasks/{task_id}/complete')

    with allure.step("Attempt to uncomplete first user's task as second user"):
        response = secondary_auth_client.patch(f'/api/tasks/{task_id}/uncomplete',
                                                handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify task remains completed for original user"):
        retrieved = auth_client.get(f'/api/tasks/{task_id}')
        assert retrieved['completed'] is True