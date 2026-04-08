import pytest
import allure


@allure.feature('Routines')
@allure.story('Delete Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_routine_returns_204(auth_client):
    """Delete routine returns 204 No Content"""
    with allure.step("Create routine to delete"):
        created = auth_client.post('/api/routines', {
            "title": "Routine to Delete"
        })
        routine_id = created['id']

    with allure.step("Delete routine"):
        response = auth_client.delete(f'/api/routines/{routine_id}',
                                      handle_response=False)

    with allure.step("Verify 204 No Content response"):
        assert response.status_code == 204
        assert response.json is None


@allure.feature('Routines')
@allure.story('Delete Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_routine_actually_removes_it(auth_client):
    """Delete routine actually removes it from the system"""
    with allure.step("Create routine to delete"):
        created = auth_client.post('/api/routines', {
            "title": "Routine to Delete"
        })
        routine_id = created['id']

    with allure.step("Delete routine"):
        delete_response = auth_client.delete(f'/api/routines/{routine_id}',
                                             handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify routine no longer exists"):
        get_response = auth_client.get(f'/api/routines/{routine_id}',
                                       handle_response=False)
        assert get_response.status_code == 404

    with allure.step("Verify routine not in list"):
        list_response = auth_client.get('/api/routines')
        routines = list_response.json
        routine_ids = [routine['id'] for routine in routines]
        assert routine_id not in routine_ids


@allure.feature('Routines')
@allure.story('Delete Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_routine_with_sessions_cascade(auth_client):
    """Delete routine with sessions cascade deletes all sessions"""
    with allure.step("Create routine with RRULE"):
        routine = auth_client.post('/api/routines', {
            "title": "Routine with Sessions",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Generate sessions for routine"):
        sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": "2026-04-01",
                "end_date": "2026-04-03"
            }
        )
        sessions = sessions_response.json
        assert len(sessions) >= 2, "Should have generated at least 2 sessions"
        session_ids = [session['id'] for session in sessions]

    with allure.step("Delete routine"):
        delete_response = auth_client.delete(f'/api/routines/{routine_id}',
                                             handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify all sessions were cascade deleted"):
        for session_id in session_ids:
            session_response = auth_client.get(f'/api/sessions/{session_id}',
                                               handle_response=False)
            assert session_response.status_code == 404, \
                f"Session {session_id} should have been deleted with routine"


@allure.feature('Routines')
@allure.story('Delete Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_routine(auth_client):
    """Delete nonexistent routine returns 404"""
    with allure.step("Attempt to delete nonexistent routine"):
        response = auth_client.delete('/api/routines/999999',
                                      handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert "routine 999999 not found" in response.json['error'].lower()


@allure.feature('Routines')
@allure.story('Delete Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.delete
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_user_routine(auth_client, secondary_auth_client):
    """Delete another user's routine returns 404"""
    with allure.step("Secondary user creates routine"):
        secondary_routine = secondary_auth_client.post('/api/routines', {
            "title": "Secondary User Routine"
        })
        secondary_routine_id = secondary_routine['id']

    with allure.step("Primary user attempts to delete secondary user's routine"):
        response = auth_client.delete(f'/api/routines/{secondary_routine_id}',
                                      handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify routine still exists for secondary user"):
        verify_response = secondary_auth_client.get(
            f'/api/routines/{secondary_routine_id}'
        )
        assert verify_response['id'] == secondary_routine_id

    with allure.step("Verify error message"):
        assert f"routine {secondary_routine_id} not found" in response.json['error'].lower()
