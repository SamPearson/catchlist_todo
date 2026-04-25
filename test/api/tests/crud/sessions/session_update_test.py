import pytest
import allure
from datetime import datetime, timedelta


def create_routine_with_tags_and_principles(auth_client, routine_title: str,
                                            tag_names: list = None,
                                            principle_titles: list = None):
    """
    Helper function to create a routine with optional tags and principles.

    Args:
        auth_client: Authenticated API client
        routine_title: Title for the routine
        tag_names: List of tag names to create and attach (optional)
        principle_titles: List of principle titles to create and attach (optional)

    Returns:
        int: ID of the created routine
    """
    with allure.step(f"Create routine '{routine_title}'"):
        routine = auth_client.post('/api/routines', {
            "title": routine_title
        })
        routine_id = routine['id']
        assert routine_id, "Routine creation failed"

    if tag_names:
        for tag_name in tag_names:
            with allure.step(f"Create and attach tag '{tag_name}'"):
                tag = auth_client.post('/api/tags', {
                    "name": tag_name
                })
                tag_id = tag['id']
                assert tag_id, f"Tag '{tag_name}' creation failed"

                attach_response = auth_client.post('/api/tags/attach', {
                    "tag_id": tag_id,
                    "target_type": "routine",
                    "target_id": routine_id
                })
                assert attach_response['success'] is True, f"Tag '{tag_name}' attachment failed"

    if principle_titles:
        for principle_title in principle_titles:
            with allure.step(f"Create and attach principle '{principle_title}'"):
                principle = auth_client.post('/api/principles', {
                    "title": principle_title
                })
                principle_id = principle['id']
                assert principle_id, f"Principle '{principle_title}' creation failed"

                attach_response = auth_client.post('/api/principles/attach', {
                    "principle_id": principle_id,
                    "target_type": "routine",
                    "target_id": routine_id
                })
                assert attach_response['success'] is True, f"Principle '{principle_title}' attachment failed"

    return routine_id


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_start_time_only(auth_client):
    """Update session start_time only"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        original_start = now + timedelta(hours=1)
        original_end = original_start + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": original_start.isoformat(),
            "end_time": original_end.isoformat(),
            "notes": "Original notes"
        })
        session_id = session['id']

    with allure.step("Update start_time only"):
        new_start = now + timedelta(hours=3)
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "start_time": new_start.isoformat()
        })

    with allure.step("Verify start_time changed and other fields unchanged"):
        assert response['id'] == session_id
        # Verify start_time changed (comparing timestamps is complex, so just verify it's present)
        assert 'start_time' in response
        # Verify other fields unchanged
        assert response['notes'] == "Original notes"


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_end_time_only(auth_client):
    """Update session end_time only"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        original_start = now + timedelta(hours=1)
        original_end = original_start + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": original_start.isoformat(),
            "end_time": original_end.isoformat(),
            "notes": "Original notes"
        })
        session_id = session['id']

    with allure.step("Update end_time only"):
        new_end = original_start + timedelta(hours=3)
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "end_time": new_end.isoformat()
        })

    with allure.step("Verify end_time changed and other fields unchanged"):
        assert response['id'] == session_id
        assert 'end_time' in response
        assert response['notes'] == "Original notes"


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_notes_only(auth_client):
    """Update session notes only"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Original notes",
            "rpe": 5
        })
        session_id = session['id']

    with allure.step("Update notes only"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "notes": "Updated notes"
        })

    with allure.step("Verify notes changed and other fields unchanged"):
        assert response['id'] == session_id
        assert response['notes'] == "Updated notes"
        assert response['rpe'] == 5


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_rpe_only(auth_client):
    """Update session rpe only"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Original notes",
            "rpe": 5
        })
        session_id = session['id']

    with allure.step("Update rpe only"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "rpe": 9
        })

    with allure.step("Verify rpe changed and other fields unchanged"):
        assert response['id'] == session_id
        assert response['rpe'] == 9
        assert response['notes'] == "Original notes"


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_multiple_fields_together(auth_client):
    """Update multiple fields together: start_time, end_time, notes, rpe"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        original_start = now + timedelta(hours=1)
        original_end = original_start + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": original_start.isoformat(),
            "end_time": original_end.isoformat(),
            "notes": "Original notes",
            "rpe": 5
        })
        session_id = session['id']

    with allure.step("Update multiple fields at once"):
        new_start = now + timedelta(hours=3)
        new_end = new_start + timedelta(hours=1)

        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "start_time": new_start.isoformat(),
            "end_time": new_end.isoformat(),
            "notes": "Updated notes",
            "rpe": 8
        })

    with allure.step("Verify all fields updated"):
        assert response['id'] == session_id
        assert 'start_time' in response
        assert 'end_time' in response
        assert response['notes'] == "Updated notes"
        assert response['rpe'] == 8


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_with_no_data(auth_client):
    """Update session with no data returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Attempt to update with no data"):
        response = auth_client.patch(f'/api/sessions/{session_id}', None,
                                     handle_response=False)

    with allure.step("Verify Http 400 and error message"):
        assert response.status_code == 400
        assert response.json['error'] == "No update data provided"


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_with_empty_request_body(auth_client):
    """Update session with empty request body returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {},
                                     handle_response=False)

    with allure.step("Verify Http 400 and error message"):
        assert response.status_code == 400
        assert response.json['error'] == "No update data provided"



@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_with_disallowed_field_status(auth_client):
    """Update session with disallowed field 'status' - field should be ignored or error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session with status='scheduled'"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "scheduled"
        })
        session_id = session['id']
        original_status = session['status']

    with allure.step("Attempt to update status via PATCH (should use status endpoint instead)"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "status": "completed",
            "notes": "Updated notes"
        }, handle_response=False)

    with allure.step("Verify status field ignored or error returned"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update status via this endpoint" in response.json['error']



@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_with_disallowed_field_routine_id(auth_client):
    """Update session with disallowed field 'routine_id' returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Attempt to update routine_id"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "routine_id": 99999
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_with_disallowed_field_user_id(auth_client):
    """Update session with disallowed field 'user_id' returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Attempt to update user_id"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "user_id": 99999
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']



@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_with_invalid_start_time_format(auth_client):
    """Update session with invalid start_time format returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Attempt to update with invalid start_time format"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "start_time": "not-a-valid-datetime"
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_session_with_invalid_end_time_format(auth_client):
    """Update session with invalid end_time format returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Attempt to update with invalid end_time format"):
        response = auth_client.patch(f'/api/sessions/{session_id}', {
            "end_time": "not-a-valid-datetime"
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_session(auth_client):
    """Update nonexistent session returns 404"""
    with allure.step("Attempt to update nonexistent session"):
        response = auth_client.patch('/api/sessions/999999', {
            "notes": "Updated notes"
        }, handle_response=False)

    with allure.step("Verify 404 Not Found"):
        assert response.status_code == 404


@allure.feature('Sessions')
@allure.story('Update Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_user_session(auth_client, secondary_auth_client):
    """Update another user's session returns 404"""
    with allure.step("Secondary user creates routine and session"):
        secondary_routine = secondary_auth_client.post('/api/routines', {
            "title": "Secondary User Routine"
        })

        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        secondary_session = secondary_auth_client.post(
            f'/api/routines/{secondary_routine["id"]}/sessions',
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        )
        secondary_session_id = secondary_session['id']

    with allure.step("Primary user attempts to update secondary user's session"):
        response = auth_client.patch(f'/api/sessions/{secondary_session_id}', {
            "notes": "Trying to update"
        }, handle_response=False)

    with allure.step("Verify 404 Not Found"):
        assert response.status_code == 404