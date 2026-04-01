import pytest
import allure
from datetime import datetime, timedelta


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_title_with_cascade_past_true(auth_client):
    """Update title with cascade_past=true updates past sessions' routine_name"""
    with allure.step("Create routine with RRULE"):
        routine = auth_client.post('/api/routines', {
            "title": "Original Title",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Generate past sessions"):
        past_start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": past_start,
                "end_date": past_end
            }
        )
        sessions = sessions_response.json
        assert len(sessions) >= 2, "Should have generated past sessions"
        session_ids = [session['id'] for session in sessions]

    with allure.step("Update routine title with cascade_past=true"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"title": "Updated Title"},
            params={"cascade_past": True}
        )
        assert updated['title'] == "Updated Title"

    with allure.step("Verify past sessions' routine_name updated"):
        for session_id in session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            assert session['routine_name'] == "Updated Title", \
                f"Session {session_id} routine_name should be updated"


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_title_with_cascade_past_false(auth_client):
    """Update title with cascade_past=false leaves sessions unchanged"""
    with allure.step("Create routine with RRULE"):
        routine = auth_client.post('/api/routines', {
            "title": "Original Title",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Generate past sessions"):
        past_start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": past_start,
                "end_date": past_end
            }
        )
        sessions = sessions_response.json
        assert len(sessions) >= 2, "Should have generated past sessions"
        session_ids = [session['id'] for session in sessions]

    with allure.step("Update routine title with cascade_past=false"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"title": "Updated Title"},
            params={"cascade_past": False}
        )
        assert updated['title'] == "Updated Title"

    with allure.step("Verify sessions unchanged"):
        for session_id in session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            assert session['routine_name'] == "Original Title", \
                f"Session {session_id} routine_name should remain unchanged"


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_title_without_cascade_past_parameter(auth_client):
    """Update title without cascade_past parameter defaults to cascade_past=false"""
    with allure.step("Create routine with RRULE"):
        routine = auth_client.post('/api/routines', {
            "title": "Original Title",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Generate past sessions"):
        past_start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": past_start,
                "end_date": past_end
            }
        )
        sessions = sessions_response.json
        assert len(sessions) >= 2, "Should have generated past sessions"
        session_ids = [session['id'] for session in sessions]

    with allure.step("Update routine title without cascade parameter"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"title": "Updated Title"}
        )
        assert updated['title'] == "Updated Title"

    with allure.step("Verify sessions unchanged (default behavior)"):
        for session_id in session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            assert session['routine_name'] == "Original Title", \
                f"Session {session_id} routine_name should remain unchanged by default"


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_start_time_with_cascade_past_true(auth_client):
    """Update start_time with cascade_past=true updates past sessions' start_time"""
    with allure.step("Create routine with RRULE and times"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Generate past sessions"):
        past_start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": past_start,
                "end_date": past_end
            }
        )
        sessions = sessions_response.json
        assert len(sessions) >= 2, "Should have generated past sessions"
        session_ids = [session['id'] for session in sessions]

    with allure.step("Update routine start_time with cascade_past=true"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"start_time": "10:00"},
            params={"cascade_past": True}
        )
        assert updated['start_time'] == "10:00"

    with allure.step("Verify past sessions' start_time updated"):
        for session_id in session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            session_start_time = session['start_time'].split('T')[1][:5]  # Extract HH:MM
            assert session_start_time == "10:00", \
                f"Session {session_id} start_time should be updated to 10:00"


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_end_time_with_cascade_past_true(auth_client):
    """Update end_time with cascade_past=true updates past sessions' end_time"""
    with allure.step("Create routine with RRULE and times"):
        routine = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Generate past sessions"):
        past_start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": past_start,
                "end_date": past_end
            }
        )
        sessions = sessions_response.json
        assert len(sessions) >= 2, "Should have generated past sessions"
        session_ids = [session['id'] for session in sessions]

    with allure.step("Update routine end_time with cascade_past=true"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"end_time": "11:00"},
            params={"cascade_past": True}
        )
        assert updated['end_time'] == "11:00"

    with allure.step("Verify past sessions' end_time updated"):
        for session_id in session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            session_end_time = session['end_time'].split('T')[1][:5]  # Extract HH:MM
            assert session_end_time == "11:00", \
                f"Session {session_id} end_time should be updated to 11:00"


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_cascade_only_affects_past_sessions(auth_client):
    """Cascade only affects past sessions, not future sessions"""
    with allure.step("Create routine with RRULE"):
        routine = auth_client.post('/api/routines', {
            "title": "Original Title",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00"
        })
        routine_id = routine['id']

    with allure.step("Generate past sessions"):
        past_start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        past_sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": past_start,
                "end_date": past_end
            }
        )
        past_sessions = past_sessions_response.json
        assert len(past_sessions) >= 2, "Should have generated past sessions"
        past_session_ids = [session['id'] for session in past_sessions]

    with allure.step("Generate future sessions"):
        future_start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        future_end = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        future_sessions_response = auth_client.post(
            f'/api/routines/{routine_id}/sessions/generate',
            {
                "start_date": future_start,
                "end_date": future_end
            }
        )
        future_sessions = future_sessions_response.json
        assert len(future_sessions) >= 2, "Should have generated future sessions"
        future_session_ids = [session['id'] for session in future_sessions]

    with allure.step("Update title with cascade_past=true"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"title": "Updated Title"},
            params={"cascade_past": True}
        )
        assert updated['title'] == "Updated Title"

    with allure.step("Verify only past sessions updated"):
        for session_id in past_session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            assert session['routine_name'] == "Updated Title", \
                f"Past session {session_id} should be updated"

    with allure.step("Verify future sessions unchanged"):
        for session_id in future_session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            assert session['routine_name'] == "Original Title", \
                f"Future session {session_id} should remain unchanged"