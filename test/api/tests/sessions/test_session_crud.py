import pytest
import allure
from datetime import datetime, timedelta


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_session_with_required_fields(auth_client):
    """Create session with required fields (routine_id, start_time, end_time)"""
    with allure.step("Create a routine first"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Prepare test data"):
        start_time = datetime.utcnow().replace(microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

    with allure.step("Create new session"):
        response = auth_client.post(f'/api/routines/{routine_id}/sessions', data)

    with allure.step("Verify response structure and values"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['routine_id'] == routine_id
        assert response['start_time']
        assert response['end_time']
        assert response['completed'] is False
        assert response['notes'] is None
        assert response['rpe'] is None


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_session_with_all_fields(auth_client):
    """Create session with all fields including optional ones"""
    with allure.step("Create a routine first"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Prepare test data"):
        start_time = datetime.utcnow().replace(microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "completed": True,
            "notes": "Test session notes",
            "rpe": 7
        }

    with allure.step("Create new session"):
        response = auth_client.post(f'/api/routines/{routine_id}/sessions', data)

    with allure.step("Verify all fields"):
        assert response['completed'] is True
        assert response['notes'] == "Test session notes"
        assert response['rpe'] == 7
        assert response['duration_minutes'] == 30


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_session_by_id(auth_client):
    """Retrieve a specific session by ID"""
    with allure.step("Create test routine and session"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00",
            "end_time": "10:00"
        })

        start_time = datetime.utcnow().replace(microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        session = auth_client.post(f'/api/routines/{routine["id"]}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Test notes"
        })
        session_id = session['id']

    with allure.step("Retrieve the session"):
        retrieved = auth_client.get(f'/api/sessions/{session_id}')

    with allure.step("Verify retrieved session matches created session"):
        assert retrieved['id'] == session_id
        assert retrieved['routine_id'] == routine['id']
        assert retrieved['notes'] == "Test notes"
        assert retrieved['start_time'] == session['start_time']
        assert retrieved['end_time'] == session['end_time']


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_sessions_in_time_window(auth_client):
    """List all sessions within a time window"""
    with allure.step("Create routine and multiple sessions"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00",
            "end_time": "10:00"
        })

        base_time = datetime.utcnow().replace(microsecond=0)
        sessions = []
        for i in range(3):
            start_time = base_time + timedelta(days=i)
            end_time = start_time + timedelta(minutes=30)
            session = auth_client.post(f'/api/routines/{routine["id"]}/sessions', {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "notes": f"Session {i + 1}"
            })
            sessions.append(session)

    with allure.step("List sessions in time window"):
        window_start = base_time - timedelta(days=1)
        window_end = base_time + timedelta(days=4)
        response = auth_client.get('/api/sessions', {
            "start": window_start.isoformat(),
            "end": window_end.isoformat()
        })

    with allure.step("Verify response"):
        assert isinstance(response, list)
        assert len(response) >= 3
        session_ids = [s['id'] for s in response]
        for session in sessions:
            assert session['id'] in session_ids


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_session(auth_client):
    """Update session fields"""
    with allure.step("Create test routine and session"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00",
            "end_time": "10:00"
        })

        start_time = datetime.utcnow().replace(microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        session = auth_client.post(f'/api/routines/{routine["id"]}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })

    with allure.step("Update session"):
        updated = auth_client.put(f'/api/sessions/{session["id"]}', {
            "completed": True,
            "notes": "Updated notes",
            "rpe": 8
        })

    with allure.step("Verify updates"):
        assert updated['id'] == session['id']
        assert updated['completed'] is True
        assert updated['notes'] == "Updated notes"
        assert updated['rpe'] == 8
        assert updated['start_time'] == session['start_time']
        assert updated['end_time'] == session['end_time']


@allure.feature('Sessions')
@allure.story('CRUD Operations')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_session(auth_client):
    """Delete a session"""
    with allure.step("Create test routine and session"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00",
            "end_time": "10:00"
        })

        start_time = datetime.utcnow().replace(microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        session = auth_client.post(f'/api/routines/{routine["id"]}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })

    with allure.step("Delete session"):
        response = auth_client.delete(f'/api/sessions/{session["id"]}',
                                      handle_response=False)

    with allure.step("Verify deletion"):
        assert response.status_code == 204

        # Verify session no longer exists
        get_response = auth_client.get(f'/api/sessions/{session["id"]}',
                                       handle_response=False)
        assert get_response.status_code == 404