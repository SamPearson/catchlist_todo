"""
Extended tests for Create Soft Commitment with Direct Timeframe Reference
(POST /api/commitments/soft with timeframe_id)

Tests creation of soft commitments using an existing timeframe_id.
"""

import pytest
import allure


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_all_fields(auth_client):
    """Create soft commitment with all optional fields populated"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Create timeframe"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        timeframe_id = timeframe['id']

    with allure.step("Create soft commitment with all fields"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe_id,
            "status": "planned",
            "notes": "Detailed notes about this commitment"
        })

    with allure.step("Verify all fields set correctly"):
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task_id
        assert commitment['timeframe_id'] == timeframe_id
        assert commitment['status'] == "planned"
        assert commitment['notes'] == "Detailed notes about this commitment"
        assert commitment['start_at'] is None # Soft commitments pin to timeframes, not times
        assert commitment['due_at'] is None # Soft commitments pin to timeframes, not times


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_verifies_defaults(auth_client):
    """Verify status defaults to 'planned'"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "month",
            "reference_date": "2025-06-15"
        })

    with allure.step("Create soft commitment without status field"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id']
        })

    with allure.step("Verify status defaults to 'planned'"):
        assert commitment['status'] == "planned"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_status_done(auth_client):
    """Verify status can be set to 'done'"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "day",
            "reference_date": "2025-06-08"
        })

    with allure.step("Create soft commitment with status 'done'"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id'],
            "status": "done"
        })

    with allure.step("Verify status is 'done'"):
        assert commitment['status'] == "done"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_status_skipped(auth_client):
    """Verify status can be set to 'skipped'"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Create soft commitment with status 'skipped'"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id'],
            "status": "skipped"
        })

    with allure.step("Verify status is 'skipped'"):
        assert commitment['status'] == "skipped"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_status_canceled(auth_client):
    """Verify status can be set to 'canceled'"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "season",
            "reference_date": "2025-06-15"
        })

    with allure.step("Create soft commitment with status 'canceled'"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id'],
            "status": "canceled"
        })

    with allure.step("Verify status is 'canceled'"):
        assert commitment['status'] == "canceled"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_status_missed(auth_client):
    """Verify status can be set to 'missed'"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "year",
            "reference_date": "2025-06-15"
        })

    with allure.step("Create soft commitment with status 'missed'"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id'],
            "status": "missed"
        })

    with allure.step("Verify status is 'missed'"):
        assert commitment['status'] == "missed"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_for_task_target(auth_client):
    """Verify target_type='task' works"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Create soft commitment for task"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id']
        })

    with allure.step("Verify commitment created for task"):
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task['id']


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_for_project_target(auth_client):
    """Verify target_type='project' works"""

    with allure.step("Create project and timeframe"):
        project = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "month",
            "reference_date": "2025-06-15"
        })

    with allure.step("Create soft commitment for project"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "project",
            "target_id": project['id'],
            "timeframe_id": timeframe['id']
        })

    with allure.step("Verify commitment created for project"):
        assert commitment['target_type'] == "project"
        assert commitment['target_id'] == project['id']


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_for_routine_target(auth_client):
    """Verify target_type='routine' works"""

    with allure.step("Create routine and timeframe"):
        routine = auth_client.post('/api/routines', {
            "title": "Test routine"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Create soft commitment for routine"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "routine",
            "target_id": routine['id'],
            "timeframe_id": timeframe['id']
        })

    with allure.step("Verify commitment created for routine"):
        assert commitment['target_type'] == "routine"
        assert commitment['target_id'] == routine['id']


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_for_session_target(auth_client):
    """Verify target_type='session' works"""

    with allure.step("Create routine and generate session"):
        routine = auth_client.post('/api/routines', {
            "title": "Test routine"
        })

        routine_id = routine['id']

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": "2026-02-01T08:00:00",
            "end_time": "2026-02-01T08:15:00"
        })

        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Create soft commitment for session"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "session",
            "target_id": session['id'],
            "timeframe_id": timeframe['id']
        })

    with allure.step("Verify commitment created for session"):
        assert commitment['target_type'] == "session"
        assert commitment['target_id'] == session['id']


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_without_target_type(auth_client):
    """Verify 400 error when target_type is missing"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Attempt to create commitment without target_type"):
        response = auth_client.post('/api/commitments/soft', {
            "target_id": task['id'],
            "timeframe_id": timeframe['id']
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message text"):
        assert "Missing required fields: target_type" in response["error"]


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_without_target_id(auth_client):
    """Verify 400 error when target_id is missing"""

    with allure.step("Create timeframe"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Attempt to create commitment without target_id"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "timeframe_id": timeframe['id']
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message text"):
        assert "Missing required fields: target_id" in response["error"]



@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_without_timeframe_specification(auth_client):
    """Verify 400 error when no timeframe specification provided"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment without timeframe_id or kind/date"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id']
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message text"):
        assert ("Must provide either 'timeframe_id' OR "
                "both 'timeframe_kind' and 'reference_date'.") in response["error"]


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_empty_request_body(auth_client):
    """Verify 400 error with empty request body"""

    with allure.step("Attempt to create commitment with empty body"):
        response = auth_client.post('/api/commitments/soft', {},
                                    handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    # Not verifying error text here because there would be many errors.
    # not willing to fail a test based on which error comes up first.


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_nonexistent_target(auth_client):
    """Verify 404 error when target does not exist"""

    with allure.step("Create timeframe"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Attempt to create commitment with non-existent task"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": 999999,
            "timeframe_id": timeframe['id']
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404

    with allure.step("Assert error message"):
        assert "Target not found" in response["error"]

@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_nonexistent_timeframe(auth_client):
    """Verify 404 error when timeframe does not exist"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment with non-existent timeframe"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": 999999
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404

    with allure.step("Assert error message"):
        assert "Timeframe not found" in response["error"]



@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_another_user_target(auth_client, secondary_auth_client):
    """Verify 404 error when target belongs to another user"""

    with allure.step("Secondary user creates task"):
        secondary_task = secondary_auth_client.post('/api/tasks', {
            "title": "Secondary user task"
        })
        secondary_task_id = secondary_task['id']

    with allure.step("Primary user creates timeframe"):
        primary_timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Primary user attempts to commit to secondary user's task"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": secondary_task_id,
            "timeframe_id": primary_timeframe['id']
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404

    with allure.step("Assert error message"):
        assert "Target not found" in response["error"]



@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_another_user_timeframe(auth_client, secondary_auth_client):
    """Verify 404 error when timeframe belongs to another user"""

    with allure.step("Primary user creates task"):
        primary_task = auth_client.post('/api/tasks', {
            "title": "Primary user task"
        })

    with allure.step("Secondary user creates timeframe"):
        secondary_timeframe = secondary_auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        secondary_timeframe_id = secondary_timeframe['id']

    with allure.step("Primary user attempts to use secondary user's timeframe"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": primary_task['id'],
            "timeframe_id": secondary_timeframe_id
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404

    with allure.step("Assert error message"):
        assert "Timeframe not found" in response["error"]



@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_invalid_status(auth_client):
    """Verify 400 error when status is invalid"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Attempt to create commitment with invalid status"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id'],
            "status": "invalid_status"
        }, handle_response = False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message text"):
        assert "Invalid status" in response["error"]


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Direct Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_duplicate_soft_commitment(auth_client):
    """Same target and timeframe returns 409 conflict"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Create first commitment"):
        first_commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id']
        })
        assert first_commitment['id']

    with allure.step("Attempt to create duplicate commitment"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id']
        }, handle_response=False)

    with allure.step("Verify 409 conflict response"):
        assert response.status_code == 409

    with allure.step("Verify error message text"):
        assert ("Soft commitment already exists "
                "for this target and timeframe") in response["error"]
