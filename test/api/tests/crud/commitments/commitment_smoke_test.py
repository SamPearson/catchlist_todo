# test/api/tests/commitments/commitments_smoke_test.py
"""
Smoke tests for Commitments API - Critical Path Validation

These tests validate that basic commitment functionality works at all.
If any of these fail, the commitments system is essentially unusable.
"""

import pytest
import allure


@allure.feature('Commitments')
@allure.story('CRUD Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_soft_commitment_with_timeframe_id(auth_client):
    """Create a soft commitment with timeframe_id"""

    with allure.step("Create a task to commit"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task for soft commitment"
        })
        task_id = task['id']

    with allure.step("Create a timeframe to commit to"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        timeframe_id = timeframe['id']

    with allure.step("Create soft commitment"):
        commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe_id
        })

    with allure.step("Verify commitment created successfully"):
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task_id
        assert commitment['timeframe_id'] == timeframe_id
        assert commitment['status'] == "planned"
        assert commitment['start_at'] is None
        assert commitment['due_at'] is None


@allure.feature('Commitments')
@allure.story('CRUD Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_hard_commitment(auth_client):
    """Create a hard commitment with due_at"""

    with allure.step("Create a task to commit"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task for hard commitment"
        })
        task_id = task['id']

    with allure.step("Create hard commitment with due_at"):
        commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task_id,
            "due_at": "2025-06-08T17:00:00"
        })

    with allure.step("Verify commitment created successfully"):
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task_id
        assert commitment['status'] == "planned"
        assert commitment['due_at'] is not None # Soft commitments have no due_at
        assert commitment['timeframe_id']  # Should implicitly create day timeframe


@allure.feature('Commitments')
@allure.story('CRUD Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_commitments(auth_client):
    """List commitments returns both soft and hard commitments"""
    
    with allure.step("Create two tasks"):
        task1 = auth_client.post('/api/tasks', {
            "title": "Task for soft commitment"
        })
        task1_id = task1['id']
        
        task2 = auth_client.post('/api/tasks', {
            "title": "Task for hard commitment"
        })
        task2_id = task2['id']
    
    with allure.step("Create a timeframe for soft commitment"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        timeframe_id = timeframe['id']
    
    with allure.step("Create soft commitment"):
        soft_commitment = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task1_id,
            "timeframe_id": timeframe_id
        })
        soft_commitment_id = soft_commitment['id']
    
    with allure.step("Create hard commitment"):
        hard_commitment = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": task2_id,
            "due_at": "2025-06-08T17:00:00"
        })
        hard_commitment_id = hard_commitment['id']
    
    with allure.step("List all commitments"):
        response = auth_client.get('/api/commitments')
        commitments = response.json
    
    with allure.step("Verify both commitments appear in list"):
        assert isinstance(commitments, list)
        assert len(commitments) >= 2
        commitment_ids = [c['id'] for c in commitments]
        assert soft_commitment_id in commitment_ids
        assert hard_commitment_id in commitment_ids


@allure.feature('Commitments')
@allure.story('CRUD Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_commitment_by_id(auth_client):
    """Get commitment by ID returns full object"""

    with allure.step("Create a task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task for get"
        })
        task_id = task['id']

    with allure.step("Create a timeframe"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "month",
            "reference_date": "2025-06-15"
        })
        timeframe_id = timeframe['id']

    with allure.step("Create soft commitment"):
        created = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe_id,
            "notes": "Test notes"
        })
        commitment_id = created['id']

    with allure.step("Get commitment by ID"):
        commitment = auth_client.get(f'/api/commitments/{commitment_id}')

    with allure.step("Verify full commitment object returned"):
        assert commitment['id'] == commitment_id
        assert commitment['target_type'] == "task"
        assert commitment['target_id'] == task_id
        assert commitment['timeframe_id'] == timeframe_id
        assert commitment['status'] == "planned"
        assert commitment['notes'] == "Test notes"



@allure.feature('Commitments')
@allure.story('CRUD Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_commitment_status(auth_client):
    """Update commitment status"""

    with allure.step("Create a task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task for status update"
        })
        task_id = task['id']

    with allure.step("Create a timeframe"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "week",
            "reference_date": "2025-06-08"
        })
        timeframe_id = timeframe['id']

    with allure.step("Create soft commitment"):
        created = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe_id
        })
        commitment_id = created['id']
        assert created['status'] == "planned"

    with allure.step("Update status to done"):
        updated = auth_client.patch(f'/api/commitments/{commitment_id}', {
            "status": "done"
        })

    with allure.step("Verify status updated"):
        assert updated['id'] == commitment_id
        assert updated['status'] == "done"


@allure.feature('Commitments')
@allure.story('CRUD Operations')
@pytest.mark.commitments
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_commitment(auth_client):
    """Delete commitment"""

    with allure.step("Create a task"):
        task = auth_client.post('/api/tasks', {
            "title": "Test task for deletion"
        })
        task_id = task['id']

    with allure.step("Create a timeframe"):
        timeframe = auth_client.post('/api/timeframes', {
            "kind": "day",
            "reference_date": "2025-06-08"
        })
        timeframe_id = timeframe['id']

    with allure.step("Create soft commitment"):
        created = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe_id
        })
        commitment_id = created['id']

    with allure.step("Delete commitment"):
        response = auth_client.delete(f'/api/commitments/{commitment_id}',
                                      handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204

    with allure.step("Verify commitment no longer exists"):
        get_response = auth_client.get(f'/api/commitments/{commitment_id}',
                                       handle_response=False)
        assert get_response.status_code == 404