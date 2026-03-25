"""
Extended tests for Create Hard Commitment
(POST /api/commitments/hard)

Tests creation of hard commitments with specific due times that auto-derive
day timeframes.
"""

import pytest
import allure


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_with_all_fields(auth_client):
    """Create hard commitment with all optional fields populated"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Create hard commitment with all fields"):
        due_timestamp = "2025-06-08T17:00:00"
        start_timestamp = "2025-06-08T09:00:00"
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task_id,
            "due_at": "2025-06-08T17:00:00",
            "start_at": "2025-06-08T09:00:00",
            "status": "planned",
            "notes": "Complete by 5pm"
        })

    with allure.step("Verify all fields set correctly"):
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task_id
        assert commitment['status'] == "planned"
        assert commitment['notes'] == "Complete by 5pm"
        assert due_timestamp in commitment['due_at'] # Response may include tz info as well
        assert start_timestamp in commitment['start_at'] # Response may include tz info as well
        assert commitment['timeframe_id'] is not None


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_verifies_defaults(auth_client):
    """Verify status defaults to 'planned'"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create hard commitment without status field"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })

    with allure.step("Verify status defaults to 'planned'"):
        assert commitment['status'] == "planned"


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_with_due_at_only(auth_client):
    """Verify start_at is optional, only due_at required"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create hard commitment with due_at only"):
        due_timestamp = "2025-06-08T17:00:00"
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": due_timestamp
        })

    with allure.step("Verify commitment created with due_at and null start_at"):
        assert due_timestamp in commitment['due_at']
        assert commitment['start_at'] is None


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_for_task_target(auth_client):
    """Verify target_type='task' works"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create hard commitment for task"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })

    with allure.step("Verify commitment created for task"):
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task['id']


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_for_routine_target(auth_client):
    """Verify target_type='routine' works"""

    with allure.step("Create routine"):
        routine = auth_client.post('/api/routines', {
            "title": "Test routine"
        })

    with allure.step("Create hard commitment for routine"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "routine",
            "target_id": routine['id'],
            "due_at": "2025-06-08T17:00:00"
        })

    with allure.step("Verify commitment created for routine"):
        assert commitment['target_type'] == "routine"
        assert commitment['target_id'] == routine['id']


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_for_session_target(auth_client):
    """Verify target_type='session' works"""

    with allure.step("Create routine and generate session"):
        routine = auth_client.post('/api/routines', {
            "title": "Test routine"
        })

        session = auth_client.post(f'/api/routines/{routine["id"]}/sessions', {
            "start_time": "2026-02-01T08:00:00",
            "end_time": "2026-02-01T08:15:00"
        })

    with allure.step("Create hard commitment for session"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "session",
            "target_id": session['id'],
            "due_at": "2025-06-08T17:00:00"
        })

    with allure.step("Verify commitment created for session"):
        assert commitment['target_type'] == "session"
        assert commitment['target_id'] == session['id']


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_for_project_target(auth_client):
    """Verify 400 error when trying to create hard commitment for project"""

    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test project"
        })

    with allure.step("Attempt to create hard commitment for project"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "project",
            "target_id": project['id'],
            "due_at": "2025-06-08T17:00:00"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Projects can only have soft commitments" in response['error']


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_without_target_type(auth_client):
    """Verify 400 error when target_type is missing"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment without target_type"):
        response = auth_client.post('/api/commitments/hard', {
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Missing required fields: target_type"


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_without_target_id(auth_client):
    """Verify 400 error when target_id is missing"""

    with allure.step("Attempt to create commitment without target_id"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "due_at": "2025-06-08T17:00:00"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Missing required fields: target_id"


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_without_due_at(auth_client):
    """Verify 400 error when due_at is missing"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment without due_at"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id']
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Missing required fields: due_at"


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_with_invalid_due_at_format(auth_client):
    """Verify 400 error when due_at format is invalid"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment with invalid due_at format"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "06/08/2025 5:00 PM"  # Invalid format
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Invalid due_at format. Expected ISO datetime."


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_with_invalid_start_at_format(auth_client):
    """Verify 400 error when start_at format is invalid"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment with invalid start_at format"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00",
            "start_at": "9:00 AM"  # Invalid format
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Invalid start_at format. Expected ISO datetime."


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_with_nonexistent_target(auth_client):
    """Verify 404 error when target does not exist"""

    with allure.step("Attempt to create commitment with non-existent task"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": 999999,
            "due_at": "2025-06-08T17:00:00"
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert "Target not found" in response['error']


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_with_another_user_target(auth_client, secondary_auth_client):
    """Verify 404 error when target belongs to another user"""

    with allure.step("Secondary user creates task"):
        secondary_task = secondary_auth_client.post('/api/tasks', {
            "title": "Secondary user task"
        })
        secondary_task_id = secondary_task['id']

    with allure.step("Primary user attempts to create hard commitment for secondary user's task"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": secondary_task_id,
            "due_at": "2025-06-08T17:00:00"
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert "Target not found" in response['error']

@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_auto_derives_day_timeframe(auth_client):
    """Verify timeframe_id is automatically set to day containing due_at"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create hard commitment with due_at"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })

    with allure.step("Verify timeframe_id is populated"):
        timeframe_id = commitment['timeframe_id']
        assert timeframe_id is not None

    with allure.step("Verify timeframe is a day timeframe"):
        timeframe = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe['kind'] == "day"


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_with_user_timezone_not_configured(auth_client):
    """Verify hard commitment works when user timezone not configured (defaults to UTC)"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create hard commitment without explicit timezone"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })

    with allure.step("Verify commitment created successfully"):
        assert commitment['id']
        assert commitment['due_at'] is not None


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_duplicate_hard_commitment(auth_client):
    """Same target and day returns 409 conflict"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create first hard commitment"):
        first_commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        assert first_commitment['id']

    with allure.step("Attempt to create duplicate commitment on same day"):
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T09:00:00"  # Different time, same day
        }, handle_response=False)

    with allure.step("Verify 409 conflict response"):
        assert response.status_code == 409

    with  allure.step("Verify error message"):
        assert response['error'] == "This entity is already committed to this timeframe."


@allure.feature('Commitments')
@allure.story('Create Hard Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_hard_commitment_converts_provided_timezone_to_utc(auth_client):
    """Verify due_at is accepted in specified timezone and stored/returned correctly"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create hard commitment with local time"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T14:30:00",
            "timezone": "America/Chicago" # This specifies the commitment's timezone, not the user's
        })

    with allure.step("Verify due_at is returned with timezone offset"):
        # The user's timezone is UTC by default, so the timestamp should be returned in UTC.
        utc_converted_timestamp = "2025-06-08T19:30:00+00:00"
        assert commitment['due_at'] == utc_converted_timestamp
