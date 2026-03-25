"""
Extended tests for Update Commitment
(PATCH /api/commitments/{id})

Tests updating commitment fields including status, notes, and datetime fields.
"""

import pytest
import allure


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_status_to_planned(auth_client):
    """Update commitment status to 'planned'"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00",
            "status": "done"
        })
        commitment_id = commitment['id']

    with allure.step("Update status to 'planned'"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "planned"
        })

    with allure.step("Verify status updated"):
        assert updated['status'] == "planned"


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_status_to_done(auth_client):
    """Update commitment status to 'done'"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update status to 'done'"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "done"
        })

    with allure.step("Verify status updated"):
        assert updated['status'] == "done"


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_status_to_skipped(auth_client):
    """Update commitment status to 'skipped'"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update status to 'skipped'"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "skipped"
        })

    with allure.step("Verify status updated"):
        assert updated['status'] == "skipped"


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_status_to_canceled(auth_client):
    """Update commitment status to 'canceled'"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update status to 'canceled'"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "canceled"
        })

    with allure.step("Verify status updated"):
        assert updated['status'] == "canceled"


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_status_to_missed(auth_client):
    """Update commitment status to 'missed'"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update status to 'missed'"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "missed"
        })

    with allure.step("Verify status updated"):
        assert updated['status'] == "missed"


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_notes(auth_client):
    """Verify notes field can be updated"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00",
            "notes": "Original notes"
        })
        commitment_id = commitment['id']

    with allure.step("Update notes"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "notes": "Updated notes about progress"
        })

    with allure.step("Verify notes updated"):
        assert updated['notes'] == "Updated notes about progress"


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_status_and_notes_together(auth_client):
    """Verify status and notes can be updated together"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00",
            "status": "planned",
            "notes": "Original notes"
        })
        commitment_id = commitment['id']

    with allure.step("Update status and notes together"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "done",
            "notes": "Completed successfully"
        })

    with allure.step("Verify both fields updated"):
        assert updated['status'] == "done"
        assert updated['notes'] == "Completed successfully"


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_due_at_on_hard_commitment(auth_client):
    """Verify due_at can be changed on hard commitment"""

    with allure.step("Create task and hard commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update due_at"):
        updated_due_time = "2025-06-09T14:00:00"
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "due_at": updated_due_time
        })

    with allure.step("Verify due_at changed"):
        assert updated_due_time in updated['due_at']


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_start_at_on_hard_commitment(auth_client):
    """Verify start_at can be changed on hard commitment"""

    with allure.step("Create task and hard commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00",
            "start_at": "2025-06-08T09:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update start_at"):
        updated_start_time = "2025-06-09T10:00:00"
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "start_at": updated_start_time
        })

    with allure.step("Verify start_at changed"):
        assert updated_start_time in updated['start_at']


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_due_at_and_start_at_together(auth_client):
    """Verify due_at and start_at can be updated together"""

    with allure.step("Create task and hard commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00",
            "start_at": "2025-06-08T09:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update both due_at and start_at"):
        update_due_time =  "2025-06-09T15:00:00"
        updated_start_time = "2025-06-09T10:00:00"
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "due_at": "2025-06-09T15:00:00",
            "start_at": "2025-06-09T10:00:00"
        })

    with allure.step("Verify both fields updated"):
        assert update_due_time in updated['due_at']
        assert updated_start_time in updated['start_at']


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_clear_due_at_with_null(auth_client):
    """Verify due_at can be cleared with null"""

    with allure.step("Create task and hard commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Clear due_at by setting to null"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "due_at": None
        })

    with allure.step("Verify due_at is null"):
        assert updated['due_at'] is None


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_clear_start_at_with_null(auth_client):
    """Verify start_at can be cleared with null"""

    with allure.step("Create task and hard commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00",
            "start_at": "2025-06-08T09:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Clear start_at by setting to null"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "start_at": None
        })

    with allure.step("Verify start_at is null"):
        assert updated['start_at'] is None


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_with_invalid_status(auth_client):
    """Verify 400 error when status is invalid"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Attempt to update with invalid status"):
        response = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "in_progress"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Invalid status" in response['error']


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_with_invalid_due_at_format(auth_client):
    """Verify 400 error when due_at format is invalid"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Attempt to update with invalid due_at format"):
        response = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "due_at": "06/08/2025"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Invalid due_at format" in response['error']


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_with_invalid_start_at_format(auth_client):
    """Verify 400 error when start_at format is invalid"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Attempt to update with invalid start_at format"):
        response = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "start_at": "9:00 AM"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Invalid start_at format" in response['error']

@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_with_no_data(auth_client):
    """Verify 400 error when no data provided"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Attempt to update with no fields"):
        response = auth_client.patch(f'/api/commitments/{commitment_id}', {
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "At least one editable field required" in response['error']



@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_with_empty_request_body(auth_client):
    """Verify 400 error with empty request body"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.patch(f'/api/commitments/{commitment_id}', {},
                                     handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "At least one editable field required" in response['error']


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_commitment_with_user_timezone_not_configured(auth_client):
    """Verify update works when user timezone not configured (defaults to UTC)"""

    with allure.step("Create task and commitment"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = commitment['id']

    with allure.step("Update due_at without explicit timezone"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "due_at": "2025-06-09T14:00:00"
        })

    with allure.step("Verify update successful"):
        assert updated['due_at'] is not None

    with allure.step("Verify due_at contains UTC offset"):
        assert "+00:00" in updated['due_at']

    with allure.step("Verify due_at is the correct time"):
        assert "2025-06-09T14:00:00" in updated['due_at']


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_commitment(auth_client):
    """Verify 404 error when commitment does not exist"""

    with allure.step("Attempt to update non-existent commitment"):
        response = auth_client.patch('/api/commitments/999999', {
            "status": "done"
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404


@allure.feature('Commitments')
@allure.story('Update Commitment')
@pytest.mark.commitments
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_user_commitment(auth_client, secondary_auth_client):
    """Verify 404 error when attempting to update another user's commitment"""

    with allure.step("Secondary user creates task and commitment"):
        secondary_task = secondary_auth_client.post('/api/tasks', {
            "title": "Secondary user task"
        })
        secondary_commitment = secondary_auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": secondary_task['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        secondary_commitment_id = secondary_commitment['id']

    with allure.step("Primary user attempts to update secondary user's commitment"):
        response = auth_client.patch(f'/api/commitments/{secondary_commitment_id}', {
            "status": "done"
        }, handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404