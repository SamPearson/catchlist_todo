import pytest
import allure
from datetime import datetime, timedelta, timezone
from test_utils.data_factories.entity_factory import create_task, create_checkin


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_note_only(auth_client):
    """Update checkin note only, occurred_at remains unchanged"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for note update test")
        original_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note",
            occurred_at=original_time
        )
        checkin_id = checkin['id']
        original_occurred_at = checkin['occurred_at']

    with allure.step("Update only the note"):
        payload = {"note": "Updated note with new information"}
        response = auth_client.put(f'/api/checkins/{checkin_id}', data=payload)

    with allure.step("Verify note changed and occurred_at unchanged"):
        assert response['id'] == checkin_id
        assert response['note'] == "Updated note with new information"
        assert response['occurred_at'] == original_occurred_at


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_occurred_at_only(auth_client):
    """Update checkin occurred_at only, note remains unchanged"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for occurred_at update test")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note for time update"
        )
        checkin_id = checkin['id']
        original_note = checkin['note']

    with allure.step("Update only the occurred_at"):
        new_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        payload = {"occurred_at": new_time}
        response = auth_client.put(f'/api/checkins/{checkin_id}', data=payload)

    with allure.step("Verify occurred_at changed and note unchanged"):
        assert response['id'] == checkin_id
        assert response['note'] == original_note
        assert response['occurred_at'] != checkin['occurred_at']


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_note_and_occurred_at_together(auth_client):
    """Update checkin note and occurred_at together"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for combined update test")
        original_time = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note",
            occurred_at=original_time
        )
        checkin_id = checkin['id']

    with allure.step("Update both note and occurred_at"):
        new_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        payload = {
            "note": "Completely updated checkin",
            "occurred_at": new_time
        }
        response = auth_client.put(f'/api/checkins/{checkin_id}', data=payload)

    with allure.step("Verify both fields changed"):
        assert response['id'] == checkin_id
        assert response['note'] == "Completely updated checkin"
        assert response['occurred_at'] != checkin['occurred_at']


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_with_empty_note(auth_client):
    """Update checkin with empty note returns 400"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for empty note validation")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note"
        )
        checkin_id = checkin['id']

    with allure.step("Attempt to update with empty note"):
        payload = {"note": ""}
        response = auth_client.put(
            f'/api/checkins/{checkin_id}',
            data=payload,
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_with_whitespace_only_note(auth_client):
    """Update checkin with whitespace-only note returns 400"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for whitespace validation")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note"
        )
        checkin_id = checkin['id']

    with allure.step("Attempt to update with whitespace-only note"):
        payload = {"note": "   \n\t   "}
        response = auth_client.put(
            f'/api/checkins/{checkin_id}',
            data=payload,
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_with_no_data(auth_client):
    """Update checkin with no data returns 400"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for no data validation")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note"
        )
        checkin_id = checkin['id']

    with allure.step("Attempt to update with no valid fields"):
        payload = {}
        response = auth_client.put(
            f'/api/checkins/{checkin_id}',
            data=payload,
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_with_empty_request_body(auth_client):
    """Update checkin with empty request body returns 400"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for empty body validation")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note"
        )
        checkin_id = checkin['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.put(
            f'/api/checkins/{checkin_id}',
            data={},
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_with_invalid_occurred_at_format(auth_client):
    """Update checkin with invalid occurred_at format returns 400"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for invalid time validation")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note"
        )
        checkin_id = checkin['id']

    with allure.step("Attempt to update with invalid occurred_at"):
        payload = {"occurred_at": "not-a-valid-timestamp"}
        response = auth_client.put(
            f'/api/checkins/{checkin_id}',
            data=payload,
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400



@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_cannot_change_target_type(auth_client):
    """Update checkin cannot change target_type (immutable)"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for immutability test")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Original note"
        )
        checkin_id = checkin['id']
        original_target_type = checkin['target_type']

    with allure.step("Attempt to update target_type"):
        payload = {
            "note": "Updated note",
            "target_type": "project"  # Try to change type
        }
        response = auth_client.put(f'/api/checkins/{checkin_id}', data=payload)

    with allure.step("Verify target_type unchanged (ignored or error)"):
        # Target_type should remain unchanged - either ignored or causes error
        # Based on API design, it's likely ignored
        assert response['target_type'] == original_target_type
        assert response['note'] == "Updated note"


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_checkin_cannot_change_target_id(auth_client):
    """Update checkin cannot change target_id (immutable)"""

    with allure.step("Create two tasks and checkin"):
        task1 = create_task(auth_client, title="Original task")
        task2 = create_task(auth_client, title="Different task")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task1['id'],
            note="Original note"
        )
        checkin_id = checkin['id']
        original_target_id = checkin['target_id']

    with allure.step("Attempt to update target_id"):
        payload = {
            "note": "Updated note",
            "target_id": task2['id']  # Try to change target
        }
        response = auth_client.put(f'/api/checkins/{checkin_id}', data=payload)

    with allure.step("Verify target_id unchanged (ignored or error)"):
        # Target_id should remain unchanged - either ignored or causes error
        assert response['target_id'] == original_target_id
        assert response['note'] == "Updated note"


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_checkin(auth_client):
    """Update nonexistent checkin returns 404"""

    with allure.step("Attempt to update nonexistent checkin"):
        payload = {"note": "Updated note"}
        response = auth_client.put(
            '/api/checkins/999999',
            data=payload,
            handle_response=False
        )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Checkins')
@allure.story('Update Checkin')
@pytest.mark.checkins
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_users_checkin(auth_client, secondary_auth_client):
    """Update another user's checkin returns 404"""

    with allure.step("Secondary user creates task and checkin"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_checkin = create_checkin(
            secondary_auth_client,
            target_type="task",
            target_id=secondary_task['id'],
            note="Secondary user's checkin"
        )
        secondary_checkin_id = secondary_checkin['id']

    with allure.step("Primary user attempts to update secondary user's checkin"):
        payload = {"note": "Attempting to update another user's checkin"}
        response = auth_client.put(
            f'/api/checkins/{secondary_checkin_id}',
            data=payload,
            handle_response=False
        )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404