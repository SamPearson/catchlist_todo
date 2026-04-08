import pytest
import allure
from datetime import datetime, timedelta


@allure.feature('Sessions')
@allure.story('Delete Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_session_returns_204(auth_client):
    """Delete session returns 204 No Content"""

    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": 'Test Routine'
        })
        routine_id = routine['id']
        assert routine_id, "Routine creation failed"


    with allure.step("Create session to delete"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Delete session"):
        response = auth_client.delete(f'/api/sessions/{session_id}',
                                      handle_response=False)

    with allure.step("Verify 204 No Content response"):
        assert response.status_code == 204
        assert response.json is None


@allure.feature('Sessions')
@allure.story('Delete Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_session_actually_removes_it(auth_client):
    """Delete session actually removes it - GET returns 404 afterward"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": 'Test Routine'
        })
        routine_id = routine['id']
        assert routine_id, "Routine creation failed"

    with allure.step("Create session to delete"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Verify session exists before deletion"):
        get_before = auth_client.get(f'/api/sessions/{session_id}')
        assert get_before['id'] == session_id

    with allure.step("Delete session"):
        delete_response = auth_client.delete(f'/api/sessions/{session_id}',
                                             handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify session no longer exists"):
        get_after = auth_client.get(f'/api/sessions/{session_id}',
                                    handle_response=False)
        assert get_after.status_code == 404


@allure.feature('Sessions')
@allure.story('Delete Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.delete
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_delete_session_cascade_deletes_commitment(auth_client):
    """Delete session cascade deletes associated commitment"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": 'Test Routine'
        })
        routine_id = routine['id']
        assert routine_id, "Routine creation failed"

    with allure.step("Create session (auto-creates commitment)"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Verify commitment exists for session"):
        commitments_response = auth_client.get('/api/commitments')
        commitments = commitments_response.json

        session_commitments = [
            c for c in commitments
            if c.get('target_type') == 'session' and c.get('target_id') == session_id
        ]

        assert len(session_commitments) == 1, "Expected exactly one commitment for session"
        commitment_id = session_commitments[0]['id']

    with allure.step("Delete session"):
        delete_response = auth_client.delete(f'/api/sessions/{session_id}',
                                             handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify commitment was cascade deleted"):
        # Try to get the commitment - should return 404
        commitment_check = auth_client.get(f'/api/commitments/{commitment_id}',
                                           handle_response=False)
        assert commitment_check.status_code == 404, \
            "Commitment should have been deleted when session was deleted"


@allure.feature('Sessions')
@allure.story('Delete Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_session(auth_client):
    """Delete nonexistent session returns 404"""
    with allure.step("Attempt to delete nonexistent session"):
        response = auth_client.delete('/api/sessions/999999',
                                      handle_response=False)

    with allure.step("Verify 404 Not Found"):
        assert response.status_code == 404


@allure.feature('Sessions')
@allure.story('Delete Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.delete
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_user_session(auth_client, secondary_auth_client):
    """Delete another user's session returns 404"""
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

    with allure.step("Primary user attempts to delete secondary user's session"):
        response = auth_client.delete(f'/api/sessions/{secondary_session_id}',
                                      handle_response=False)

    with allure.step("Verify 404 Not Found"):
        assert response.status_code == 404

    with allure.step("Verify secondary user's session still exists"):
        verify_response = secondary_auth_client.get(f'/api/sessions/{secondary_session_id}')
        assert verify_response['id'] == secondary_session_id