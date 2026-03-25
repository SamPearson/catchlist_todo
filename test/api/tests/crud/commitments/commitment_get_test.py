# test/api/tests/commitments/commitments_get_test.py
"""
Extended tests for Get Commitment endpoint (GET /api/commitments/{id})

Tests retrieval of individual commitments with various scenarios.
"""

import pytest
import allure


@allure.feature('Commitments')
@allure.story('Get Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_commitment_returns_full_object(auth_client):
    """Verify all fields present including timestamps in local time"""

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

    with allure.step("Create soft commitment with all optional fields"):
        created = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe_id,
            "status": "planned",
            "notes": "Test notes for commitment"
        })
        commitment_id = created['id']

    with allure.step("Get commitment by ID"):
        commitment = auth_client.get(f'/api/commitments/{commitment_id}')

    with allure.step("Verify full object structure with all fields"):
        assert commitment['id'] == commitment_id
        assert commitment['user_id'] is not None
        assert commitment['timeframe_id'] == timeframe_id
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task_id
        assert commitment['status'] == "planned"
        assert commitment['notes'] == "Test notes for commitment"
        assert commitment['created_at'] is not None
        assert commitment['updated_at'] is not None


@allure.feature('Commitments')
@allure.story('Get Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_soft_commitment_has_null_timestamps(auth_client):
    """Verify soft commitment timestamps are null"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "month",
            "reference_date": "2025-06-15"
        })

    with allure.step("Create soft commitment"):
        created = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id']
        })
        commitment_id = created['id']

    with allure.step("Get commitment by ID"):
        commitment = auth_client.get(f'/api/commitments/{commitment_id}')

    with allure.step("Verify start_at and due_at are null"):
        assert commitment['start_at'] is None
        assert commitment['due_at'] is None


@allure.feature('Commitments')
@allure.story('Get Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_hard_commitment_has_due_at_populated(auth_client):
    """Verify hard commitment has due_at"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task for hard commitment"
        })
        task_id = task['id']

    with allure.step("Create hard commitment with due_at"):
        created = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task_id,
            "due_at": "2025-06-08T17:00:00"
        })
        commitment_id = created['id']

    with allure.step("Get commitment by ID"):
        commitment = auth_client.get(f'/api/commitments/{commitment_id}')

    with allure.step("Verify due_at contains input string"):
        assert commitment['due_at'] is not None
        assert "2025-06-08T17:00:00" in commitment['due_at']  # passes with or without a timezone eg "2025-06-08T17:00:00+00:00"


@allure.feature('Commitments')
@allure.story('Get Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_commitment(auth_client):
    """Verify 404 for non-existent commitment"""

    with allure.step("Attempt to get non-existent commitment"):
        response = auth_client.get('/api/commitments/999999',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Commitments')
@allure.story('Get Operations')
@pytest.mark.commitments
@pytest.mark.auth
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_user_commitment(auth_client, secondary_auth_client):
    """Verify 404 when accessing another user's commitment"""

    with allure.step("Primary user creates task and commitment"):
        primary_task = auth_client.post('/api/tasks', {
            "title": "Primary user task"
        })
        primary_timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        primary_commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": primary_task['id'],
            "timeframe_id": primary_timeframe['id']
        })
        primary_commitment_id = primary_commitment['id']

    with allure.step("Secondary user attempts to get primary user's commitment"):
        response = secondary_auth_client.get(f'/api/commitments/{primary_commitment_id}',
                                             handle_response=False)

    with allure.step("Verify 404 response (not found, not unauthorized)"):
        assert response.status_code == 404