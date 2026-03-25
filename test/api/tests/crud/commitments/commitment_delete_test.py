"""
Extended tests for Delete Commitment
(DELETE /api/commitments/{id})

Tests deletion of commitments.
"""

import pytest
import allure


@allure.feature('Commitments')
@allure.story('Delete Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_commitment_returns_204(auth_client):
    """Delete commitment returns 204 No Content"""

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

    with allure.step("Delete commitment"):
        response = auth_client.delete(f'/api/commitments/{commitment_id}',
                                      handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204

    with allure.step ("Verify commitment no longer exists"):
        response = auth_client.get(f'/api/commitments/{commitment_id}',
                                   handle_response=False)
        assert response.status_code == 404


@allure.feature('Commitments')
@allure.story('Delete Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_commitment_actually_removes_it(auth_client):
    """Delete commitment actually removes it - verify GET returns 404 afterward"""

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

    with allure.step("Verify commitment exists"):
        retrieved = auth_client.get(f'/api/commitments/{commitment_id}')
        assert retrieved['id'] == commitment_id

    with allure.step("Delete commitment"):
        response = auth_client.delete(f'/api/commitments/{commitment_id}',
                                      handle_response=False)
        assert response.status_code == 204

    with allure.step("Verify commitment no longer exists"):
        response = auth_client.get(f'/api/commitments/{commitment_id}',
                                   handle_response=False)
        assert response.status_code == 404


@allure.feature('Commitments')
@allure.story('Delete Commitment')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_commitment(auth_client):
    """Verify 404 error when attempting to delete non-existent commitment"""

    with allure.step("Attempt to delete non-existent commitment"):
        response = auth_client.delete('/api/commitments/999999',
                                      handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert "Couldn't find commitment" in response['error']


@allure.feature('Commitments')
@allure.story('Delete Commitment')
@pytest.mark.commitments
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_user_commitment(auth_client, secondary_auth_client):
    """Verify 404 error when attempting to delete another user's commitment"""

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

    with allure.step("Primary user attempts to delete secondary user's commitment"):
        response = auth_client.delete(f'/api/commitments/{secondary_commitment_id}',
                                      handle_response=False)

    with allure.step("Verify 404 error response"):
        assert response.status_code == 404
        assert "Couldn't find commitment" in response['error']

    with allure.step("Verify commitment still exists for secondary user"):
        retrieved = secondary_auth_client.get(f'/api/commitments/{secondary_commitment_id}')
        assert retrieved['id'] == secondary_commitment_id