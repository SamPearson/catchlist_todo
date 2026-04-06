import pytest
import allure
from datetime import datetime, timedelta


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_basic_session(auth_client):
    """Create a basic session with start_time and end_time"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine for Session"
        })
        routine_id = routine['id']

    with allure.step("Prepare session data"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session_data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

    with allure.step("Create session"):
        response = auth_client.post(f'/api/routines/{routine_id}/sessions', session_data)

    with allure.step("Verify session created with correct data"):
        assert response['id']
        assert response['routine_id'] == routine_id
        assert response['status'] == 'scheduled'
        assert response['start_time']
        assert response['end_time']


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_sessions_in_window(auth_client):
    """List sessions in window returns created session"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine for List"
        })
        routine_id = routine['id']

    with allure.step("Create session in time window"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("List sessions in window containing created session"):
        window_start = now.isoformat()
        window_end = (now + timedelta(days=1)).isoformat()

        response = auth_client.get('/api/sessions', params={
            'start': window_start,
            'end': window_end
        })

        routines = response.json

    with allure.step("Verify created session appears in list"):
        assert isinstance(routines, list)
        session_ids = [s['id'] for s in routines]
        assert session_id in session_ids


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.get
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_session_by_id(auth_client):
    """Get session by ID returns full session object"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine for Get"
        })
        routine_id = routine['id']

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        created_session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = created_session['id']

    with allure.step("Get session by ID"):
        response = auth_client.get(f'/api/sessions/{session_id}')

    with allure.step("Verify session data"):
        assert response['id'] == session_id
        assert response['routine_id'] == routine_id
        assert response['status'] == 'scheduled'
        assert 'start_time' in response
        assert 'end_time' in response
        assert 'created_at' in response
        assert 'updated_at' in response


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_session(auth_client):
    """Update session fields"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine for Update"
        })
        routine_id = routine['id']

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Update session notes and RPE"):
        update_data = {
            "notes": "Updated session notes",
            "rpe": 7
        }
        response = auth_client.patch(f'/api/sessions/{session_id}', update_data)

    with allure.step("Verify session updated"):
        assert response['id'] == session_id
        assert response['notes'] == "Updated session notes"
        assert response['rpe'] == 7


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.delete
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_session(auth_client):
    """Delete session returns 204 and removes session"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine for Delete"
        })
        routine_id = routine['id']

    with allure.step("Create session to delete"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

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

    with allure.step("Verify session no longer exists"):
        get_response = auth_client.get(f'/api/sessions/{session_id}',
                                       handle_response=False)
        assert get_response.status_code == 404