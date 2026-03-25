import pytest
import allure


@allure.feature('Commitments')
@allure.story('List Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_commitments_returns_empty_array(auth_client):
    """New user with no commitments gets empty array"""

    with allure.step("List commitments for new user"):
        response = auth_client.get('/api/commitments')
        commitments = response.json

    with allure.step("Verify empty array returned"):
        assert isinstance(commitments, list)
        assert len(commitments) == 0


@allure.feature('Commitments')
@allure.story('List Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.list
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_list_commitments_only_returns_user_own_commitments(auth_client, secondary_auth_client):
    """Create commitments for two users, verify isolation"""

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

    with allure.step("Secondary user creates task and commitment"):
        secondary_task = secondary_auth_client.post('/api/tasks', {
            "title": "Secondary user task"
        })
        secondary_timeframe = secondary_auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        secondary_commitment = secondary_auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": secondary_task['id'],
            "timeframe_id": secondary_timeframe['id']
        })
        secondary_commitment_id = secondary_commitment['id']

    with allure.step("Primary user lists commitments"):
        primary_commitments = auth_client.get('/api/commitments')

    with allure.step("Verify primary user only sees their own commitment"):
        primary_ids = [c['id'] for c in primary_commitments]
        assert primary_commitment_id in primary_ids
        assert secondary_commitment_id not in primary_ids

    with allure.step("Secondary user lists commitments"):
        secondary_commitments = secondary_auth_client.get('/api/commitments')

    with allure.step("Verify secondary user only sees their own commitment"):
        secondary_ids = [c['id'] for c in secondary_commitments]
        assert secondary_commitment_id in secondary_ids
        assert primary_commitment_id not in secondary_ids


@allure.feature('Commitments')
@allure.story('List Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_commitments_filters_by_timeframe_id(auth_client):
    """Create commitments in different timeframes, filter by one"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Create two different timeframes"):
        timeframe1 = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        timeframe1_id = timeframe1['id']

        timeframe2 = auth_client.post('/api/timeframes', {
            "kind": "month",
            "reference_date": "2025-06-15"
        })
        timeframe2_id = timeframe2['id']

    with allure.step("Create commitment in first timeframe"):
        commitment1 = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe1_id
        })
        commitment1_id = commitment1['id']

    with allure.step("Create second task for second timeframe"):
        task2 = auth_client.post('/api/tasks', {
            "title": "Second task"
        })

        commitment2 = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task2['id'],
            "timeframe_id": timeframe2_id
        })
        commitment2_id = commitment2['id']

    with allure.step("Filter commitments by first timeframe"):
        response = auth_client.get(f'/api/commitments?timeframe_id={timeframe1_id}')
        timeframes = response.json

    with allure.step("Verify only first timeframe commitment returned"):
        assert isinstance(timeframes, list)
        filtered_ids = [c['id'] for c in timeframes]
        assert commitment1_id in filtered_ids
        assert commitment2_id not in filtered_ids

        # Verify all returned commitments have the correct timeframe
        for commitment in timeframes:
            assert commitment['timeframe_id'] == timeframe1_id


@allure.feature('Commitments')
@allure.story('List Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_commitments_with_invalid_timeframe_id(auth_client):
    """Verify 400 error when timeframe_id is not an integer"""

    with allure.step("Request commitments with invalid timeframe_id"):
        response = auth_client.get('/api/commitments?timeframe_id=invalid',
                                   handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400


@allure.feature('Commitments')
@allure.story('List Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_commitments_returns_both_soft_and_hard(auth_client):
    """Create one soft and one hard commitment, verify both returned"""

    with allure.step("Create tasks"):
        task1 = auth_client.post('/api/tasks', {
            "title": "Task for soft commitment"
        })
        task2 = auth_client.post('/api/tasks', {
            "title": "Task for hard commitment"
        })

    with allure.step("Create timeframe for soft commitment"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Create soft commitment"):
        soft_commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task1['id'],
            "timeframe_id": timeframe['id']
        })
        soft_id = soft_commitment['id']

    with allure.step("Create hard commitment"):
        hard_commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task2['id'],
            "due_at": "2025-06-08T17:00:00"
        })
        hard_id = hard_commitment['id']

    with allure.step("List all commitments"):
        response = auth_client.get('/api/commitments')
        commitments = response.json

    with allure.step("Verify both soft and hard commitments returned"):
        assert isinstance(commitments, list)
        assert len(commitments) >= 2

        commitment_ids = [c['id'] for c in commitments]
        assert soft_id in commitment_ids
        assert hard_id in commitment_ids

        # Find and verify soft commitment has no due_at/start_at
        soft = next(c for c in commitments if c['id'] == soft_id)
        assert soft['due_at'] is None
        assert soft['start_at'] is None

        # Find and verify hard commitment has due_at
        hard = next(c for c in commitments if c['id'] == hard_id)
        assert hard['due_at'] is not None