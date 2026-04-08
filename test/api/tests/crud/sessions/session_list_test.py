import pytest
import allure
from datetime import datetime, timedelta


@allure.feature('Sessions')
@allure.story('List Sessions')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_sessions_returns_only_sessions_in_window(auth_client):
    """List sessions returns only sessions within the specified time window"""
    with allure.step("Create parent routine"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = routine['id']

    with allure.step("Create session inside window"):
        now = datetime.utcnow()
        inside_start = now + timedelta(hours=2)
        inside_end = inside_start + timedelta(hours=1)

        inside_session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": inside_start.isoformat(),
            "end_time": inside_end.isoformat()
        })

    # It may seem like it would be better to create sessions in one big window, then test for sessions in a subset;
    # but creating three batches allows us to parse for known good session IDs instead of parsing for dates.
    with allure.step("Create session before window"):
        before_start = now - timedelta(days=2)
        before_end = before_start + timedelta(hours=1)

        before_session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": before_start.isoformat(),
            "end_time": before_end.isoformat()
        })

    with allure.step("Create session after window"):
        after_start = now + timedelta(days=5)
        after_end = after_start + timedelta(hours=1)

        after_session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": after_start.isoformat(),
            "end_time": after_end.isoformat()
        })

    with allure.step("List sessions in window"):
        window_start = now.isoformat()
        window_end = (now + timedelta(days=3)).isoformat()

        response = auth_client.get('/api/sessions', params={
            'start': window_start,
            'end': window_end
        })
        sessions = response.json

    with allure.step("Verify only session inside window is returned"):
        session_ids = [s['id'] for s in sessions]
        assert inside_session['id'] in session_ids, "Session inside window should be included"
        assert before_session['id'] not in session_ids, "Session before window should be excluded"
        assert after_session['id'] not in session_ids, "Session after window should be excluded"


@allure.feature('Sessions')
@allure.story('List Sessions')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_sessions_returns_empty_array(auth_client):
    """List sessions returns empty array when no sessions in window"""
    with allure.step("Query window with no sessions"):
        now = datetime.utcnow()
        window_start = (now + timedelta(days=30)).isoformat()
        window_end = (now + timedelta(days=60)).isoformat()

        response = auth_client.get('/api/sessions', params={
            'start': window_start,
            'end': window_end
        })
        sessions = response.json

    with allure.step("Verify empty array returned"):
        assert isinstance(sessions, list)
        assert len(sessions) == 0


@allure.feature('Sessions')
@allure.story('List Sessions')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_list_sessions_only_returns_user_own_sessions(auth_client, secondary_auth_client):
    """List sessions only returns user's own sessions (isolation test)"""
    with allure.step("Primary user creates routine and session"):
        primary_routine = auth_client.post('/api/routines', {
            "title": "Primary User Routine"
        })

        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        primary_session = auth_client.post(f'/api/routines/{primary_routine["id"]}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })

    with allure.step("Secondary user creates routine and session"):
        secondary_routine = secondary_auth_client.post('/api/routines', {
            "title": "Secondary User Routine"
        })

        secondary_session = secondary_auth_client.post(
            f'/api/routines/{secondary_routine["id"]}/sessions', {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            })

    with allure.step("Define time window covering both sessions"):
        window_start = now.isoformat()
        window_end = (now + timedelta(days=1)).isoformat()

    with allure.step("Primary user lists their sessions"):
        primary_response = auth_client.get('/api/sessions', params={
            'start': window_start,
            'end': window_end
        })
        primary_sessions = primary_response.json
        primary_ids = [s['id'] for s in primary_sessions]

    with allure.step("Secondary user lists their sessions"):
        secondary_response = secondary_auth_client.get('/api/sessions', params={
            'start': window_start,
            'end': window_end
        })
        secondary_sessions = secondary_response.json
        secondary_ids = [s['id'] for s in secondary_sessions]

    with allure.step("Verify user isolation"):
        assert primary_session['id'] in primary_ids, "Primary user should see their session"
        assert primary_session['id'] not in secondary_ids, "Secondary user should not see primary's session"
        assert secondary_session['id'] in secondary_ids, "Secondary user should see their session"
        assert secondary_session['id'] not in primary_ids, "Primary user should not see secondary's session"


@allure.feature('Sessions')
@allure.story('List Sessions')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_sessions_without_start_parameter(auth_client):
    """List sessions without start parameter returns 400 error"""
    with allure.step("Attempt to list sessions without start parameter"):
        now = datetime.utcnow()
        window_end = (now + timedelta(days=1)).isoformat()

        response = auth_client.get('/api/sessions', params={
            'end': window_end
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "start and end ISO dates required" in response.json['error']


@allure.feature('Sessions')
@allure.story('List Sessions')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_sessions_without_end_parameter(auth_client):
    """List sessions without end parameter returns 400 error"""
    with allure.step("Attempt to list sessions without end parameter"):
        now = datetime.utcnow()
        window_start = now.isoformat()

        response = auth_client.get('/api/sessions', params={
            'start': window_start
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "start and end ISO dates required" in response.json['error']



@allure.feature('Sessions')
@allure.story('List Sessions')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_sessions_with_invalid_start_format(auth_client):
    """List sessions with invalid start format returns 400 error"""
    with allure.step("Attempt to list sessions with invalid start format"):
        now = datetime.utcnow()
        window_end = (now + timedelta(days=1)).isoformat()

        response = auth_client.get('/api/sessions', params={
            'start': 'not-a-valid-date',
            'end': window_end
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Invalid date format" in response.json['error']


@allure.feature('Sessions')
@allure.story('List Sessions')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_sessions_with_invalid_end_format(auth_client):
    """List sessions with invalid end format returns 400 error"""
    with allure.step("Attempt to list sessions with invalid end format"):
        now = datetime.utcnow()
        window_start = now.isoformat()

        response = auth_client.get('/api/sessions', params={
            'start': window_start,
            'end': 'not-a-valid-date'
        }, handle_response=False)

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Invalid date format" in response.json['error']
