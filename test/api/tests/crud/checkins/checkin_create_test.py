import pytest
import allure
from datetime import datetime, timedelta, timezone
from utils.data_factories.entity_factory import (
    create_task,
    create_project,
    create_routine,
    create_session,
    create_calendar,
    create_checkin
)


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_all_fields(auth_client):
    """Create checkin with all fields specified"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for full checkin")
        task_id = task['id']

    with allure.step("Create checkin with all fields"):
        occurred_at = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": "Detailed progress note with all fields",
            "occurred_at": occurred_at
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify all fields returned"):
        assert response['id']
        assert response['target_type'] == "task"
        assert response['target_id'] == task_id
        assert response['note'] == "Detailed progress note with all fields"
        assert response['occurred_at']
        assert response['created_at']
        assert response['updated_at']




@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_occurred_at_in_past(auth_client):
    """Create checkin with occurred_at in the past (backdating)"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for backdating test")
        task_id = task['id']

    with allure.step("Create checkin with past occurred_at"):
        past_time = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": "This happened 5 days ago",
            "occurred_at": past_time
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify backdating worked"):
        assert response['id']
        assert response['note'] == "This happened 5 days ago"
        # occurred_at should be in the past, created_at should be recent
        assert response['occurred_at'] == past_time
        assert response['created_at']


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_occurred_at_in_future(auth_client):
    """Create checkin with occurred_at in the future (future dating)"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for future dating test")
        task_id = task['id']

    with allure.step("Create checkin with future occurred_at"):
        future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": "Planning for future event",
            "occurred_at": future_time
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify future dating worked"):
        assert response['id']
        assert response['note'] == "Planning for future event"
        assert response['occurred_at'] == future_time


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_for_task_target(auth_client):
    """Create checkin for task target type"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for task target test")
        task_id = task['id']

    with allure.step("Create checkin for task"):
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": "Task checkin"
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify task target type works"):
        assert response['id']
        assert response['target_type'] == "task"
        assert response['target_id'] == task_id


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_for_project_target(auth_client):
    """Create checkin for project target type"""

    with allure.step("Create project"):
        project = create_project(auth_client, title="Project for checkin")
        project_id = project['id']

    with allure.step("Create checkin for project"):
        payload = {
            "target_type": "project",
            "target_id": project_id,
            "note": "Project progress update"
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify project target type works"):
        assert response['id']
        assert response['target_type'] == "project"
        assert response['target_id'] == project_id


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_for_routine_target(auth_client):
    """Create checkin for routine target type"""

    with allure.step("Create calendar and routine"):
        calendar = create_calendar(auth_client, name="Test Calendar")
        routine = create_routine(
            auth_client,
            title="Test Routine",
            calendar_id=calendar['id']
        )
        routine_id = routine['id']

    with allure.step("Create checkin for routine"):
        payload = {
            "target_type": "routine",
            "target_id": routine_id,
            "note": "Routine reflection"
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify routine target type works"):
        assert response['id']
        assert response['target_type'] == "routine"
        assert response['target_id'] == routine_id


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_for_session_target(auth_client):
    """Create checkin for session target type"""

    with allure.step("Create calendar, routine, and session"):
        calendar = create_calendar(auth_client, name="Test Calendar")
        routine = create_routine(
            auth_client,
            title="Test Routine",
            calendar_id=calendar['id']
        )
        session = create_session(auth_client, routine['id'])
        session_id = session['id']

    with allure.step("Create checkin for session"):
        payload = {
            "target_type": "session",
            "target_id": session_id,
            "note": "Session went well"
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify session target type works"):
        assert response['id']
        assert response['target_type'] == "session"
        assert response['target_id'] == session_id


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_without_target_type(auth_client):
    """Create checkin without target_type returns 400"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for validation test")
        task_id = task['id']

    with allure.step("Attempt to create checkin without target_type"):
        payload = {
            "target_id": task_id,
            "note": "Missing target type"
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_without_target_id(auth_client):
    """Create checkin without target_id returns 400"""

    with allure.step("Attempt to create checkin without target_id"):
        payload = {
            "target_type": "task",
            "note": "Missing target ID"
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_without_note(auth_client):
    """Create checkin without note returns 400"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for note validation")
        task_id = task['id']

    with allure.step("Attempt to create checkin without note"):
        payload = {
            "target_type": "task",
            "target_id": task_id
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_empty_note(auth_client):
    """Create checkin with empty note returns 400"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for empty note test")
        task_id = task['id']

    with allure.step("Attempt to create checkin with empty note"):
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": ""
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_whitespace_only_note(auth_client):
    """Create checkin with whitespace-only note returns 400"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for whitespace note test")
        task_id = task['id']

    with allure.step("Attempt to create checkin with whitespace-only note"):
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": "   \n\t   "
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_invalid_target_type(auth_client):
    """Create checkin with invalid target_type returns 400"""

    with allure.step("Attempt to create checkin with invalid target_type"):
        payload = {
            "target_type": "invalid_type",
            "target_id": 123,
            "note": "Invalid target type"
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_invalid_occurred_at_format(auth_client):
    """Create checkin with invalid occurred_at format returns 400"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for occurred_at validation")
        task_id = task['id']

    with allure.step("Attempt to create checkin with invalid occurred_at"):
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": "Invalid timestamp",
            "occurred_at": "not-a-valid-timestamp"
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_with_empty_request_body(auth_client):
    """Create checkin with empty request body returns 400"""

    with allure.step("Attempt to create checkin with empty body"):
        response = auth_client.post('/api/checkins', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_for_nonexistent_target(auth_client):
    """Create checkin for nonexistent target returns 404"""

    with allure.step("Attempt to create checkin for nonexistent task"):
        payload = {
            "target_type": "task",
            "target_id": 999999,
            "note": "Target does not exist"
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Checkins')
@allure.story('Create Checkin')
@pytest.mark.checkins
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_checkin_for_another_users_target(auth_client, secondary_auth_client):
    """Create checkin for another user's target returns 404"""

    with allure.step("Secondary user creates task"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_task_id = secondary_task['id']

    with allure.step("Primary user attempts to create checkin for secondary user's task"):
        payload = {
            "target_type": "task",
            "target_id": secondary_task_id,
            "note": "Attempting to access another user's task"
        }
        response = auth_client.post('/api/checkins', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


