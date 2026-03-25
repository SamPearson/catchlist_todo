"""
Extended tests for Create Soft Commitment with Implicit Timeframe Creation
(POST /api/commitments/soft with timeframe_kind and reference_date)

Tests creation of soft commitments where the system automatically fetches or creates
the appropriate timeframe based on kind and reference_date.
"""

import pytest
import allure


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_timeframe_kind_and_reference_date(auth_client):
    """Create soft commitment with timeframe_kind and reference_date auto-creates timeframe"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        task_id = task['id']

    with allure.step("Create soft commitment with timeframe_kind and reference_date"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Verify commitment created with timeframe_id"):
        assert commitment['id']
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task_id
        assert commitment['timeframe_id'] is not None
        assert commitment['status'] == "planned"
        assert commitment['start_at'] is None
        assert commitment['due_at'] is None


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_timeframe_kind_day(auth_client):
    """Verify timeframe_kind='day' derives correct day timeframe"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create soft commitment with kind=day"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "day",
            "reference_date": "2025-06-08"
        })

    with allure.step("Verify timeframe created"):
        timeframe_id = commitment['timeframe_id']
        assert timeframe_id is not None

        # Verify we can retrieve the timeframe
        timeframe = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe['kind'] == "day"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_timeframe_kind_week(auth_client):
    """Verify timeframe_kind='week' derives correct week timeframe"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create soft commitment with kind=week"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Verify timeframe created"):
        timeframe_id = commitment['timeframe_id']
        assert timeframe_id is not None

        timeframe = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe['kind'] == "week"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_timeframe_kind_month(auth_client):
    """Verify timeframe_kind='month' derives correct month timeframe"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create soft commitment with kind=month"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "month",
            "reference_date": "2025-06-15"
        })

    with allure.step("Verify timeframe created"):
        timeframe_id = commitment['timeframe_id']
        assert timeframe_id is not None

        timeframe = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe['kind'] == "month"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_timeframe_kind_season(auth_client):
    """Verify timeframe_kind='season' derives correct season timeframe"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create soft commitment with kind=season"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "season",
            "reference_date": "2025-06-15"
        })

    with allure.step("Verify timeframe created"):
        timeframe_id = commitment['timeframe_id']
        assert timeframe_id is not None

        timeframe = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe['kind'] == "season"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_timeframe_kind_year(auth_client):
    """Verify timeframe_kind='year' derives correct year timeframe"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Create soft commitment with kind=year"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "year",
            "reference_date": "2025-06-15"
        })

    with allure.step("Verify timeframe created"):
        timeframe_id = commitment['timeframe_id']
        assert timeframe_id is not None

        timeframe = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe['kind'] == "year"


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_without_reference_date(auth_client):
    """Verify 400 error when timeframe_kind provided but reference_date missing"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment without reference_date"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "week"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_without_timeframe_kind(auth_client):
    """Verify 400 error when reference_date provided but timeframe_kind missing"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment without timeframe_kind"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "reference_date": "2025-06-08"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_invalid_reference_date_format(auth_client):
    """Verify 400 error when reference_date format is invalid"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment with invalid date format"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "week",
            "reference_date": "06/08/2025"  # Wrong format
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_invalid_timeframe_kind(auth_client):
    """Verify 400 error when timeframe_kind is invalid"""

    with allure.step("Create task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })

    with allure.step("Attempt to create commitment with invalid timeframe_kind"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_kind": "decade",  # Invalid kind
            "reference_date": "2025-06-08"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_with_both_timeframe_id_and_kind(auth_client):
    """Verify 400 error when both timeframe_id and timeframe_kind provided (conflicting approaches)"""

    with allure.step("Create task and timeframe"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task"
        })
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })

    with allure.step("Attempt to create commitment with both approaches"):
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task['id'],
            "timeframe_id": timeframe['id'],
            "timeframe_kind": "month",
            "reference_date": "2025-06-15"
        }, handle_response=False)

    with allure.step("Verify 400 error response"):
        assert response.status_code == 400


@allure.feature('Commitments')
@allure.story('Create Soft Commitment - Implicit Timeframe')
@pytest.mark.commitments
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_soft_commitment_reuses_existing_timeframe(auth_client):
    """Create two commitments with same kind/date verifies they share the same timeframe"""

    with allure.step("Create two tasks"):
        task1 = auth_client.post('/api/tasks', {
            "title": "First task"
        })
        task2 = auth_client.post('/api/tasks', {
            "title": "Second task"
        })

    with allure.step("Create first commitment with implicit timeframe"):
        commitment1 = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task1['id'],
            "timeframe_kind": "week",
            "reference_date": "2025-06-08"
        })
        timeframe_id_1 = commitment1['timeframe_id']

    with allure.step("Create second commitment with same kind and date"):
        commitment2 = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task2['id'],
            "timeframe_kind": "week",
            "reference_date": "2025-06-08"
        })
        timeframe_id_2 = commitment2['timeframe_id']

    with allure.step("Verify both commitments use the same timeframe"):
        assert timeframe_id_1 == timeframe_id_2