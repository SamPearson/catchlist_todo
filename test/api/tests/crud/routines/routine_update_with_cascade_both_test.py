import pytest
import allure
from datetime import datetime, timedelta


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_title_with_cascade_future_and_past_true(auth_client):
    """Update title with cascade_future=true and cascade_past=true updates ALL sessions"""
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

    with allure.step("Update title with both cascade parameters true"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"title": "Updated Title"},
            params={
                "cascade_future": True,
                "cascade_past": True
            }
        )
        assert updated['title'] == "Updated Title"

    with allure.step("Verify ALL sessions updated"):
        all_session_ids = past_session_ids + future_session_ids
        for session_id in all_session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            assert session['routine_name'] == "Updated Title", \
                f"Session {session_id} routine_name should be updated"


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_times_with_cascade_future_and_past_true(auth_client):
    """Update times with cascade_future=true and cascade_past=true updates ALL sessions' times"""
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

    with allure.step("Update times with both cascade parameters true"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {
                "start_time": "14:00",
                "end_time": "15:30"
            },
            params={
                "cascade_future": True,
                "cascade_past": True
            }
        )
        assert updated['start_time'] == "14:00"
        assert updated['end_time'] == "15:30"

    with allure.step("Verify ALL sessions' times updated"):
        all_session_ids = past_session_ids + future_session_ids
        for session_id in all_session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            session_start_time = session['start_time'].split('T')[1][:5]
            session_end_time = session['end_time'].split('T')[1][:5]
            assert session_start_time == "14:00", \
                f"Session {session_id} start_time should be updated to 14:00"
            assert session_end_time == "15:30", \
                f"Session {session_id} end_time should be updated to 15:30"


@allure.feature('Routines')
@allure.story('Update with Cascade')
@pytest.mark.routines
@pytest.mark.cascade
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_with_cascade_future_and_past_false(auth_client):
    """Update with cascade_future=false and cascade_past=false updates NO sessions"""
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

    with allure.step("Update title with both cascade parameters false"):
        updated = auth_client.patch(
            f'/api/routines/{routine_id}',
            {"title": "Updated Title"},
            params={
                "cascade_future": False,
                "cascade_past": False
            }
        )
        assert updated['title'] == "Updated Title"

    with allure.step("Verify NO sessions updated"):
        all_session_ids = past_session_ids + future_session_ids
        for session_id in all_session_ids:
            session = auth_client.get(f'/api/sessions/{session_id}')
            assert session['routine_name'] == "Original Title", \
                f"Session {session_id} routine_name should remain unchanged"