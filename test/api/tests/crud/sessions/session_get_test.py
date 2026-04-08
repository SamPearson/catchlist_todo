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
@allure.story('Get Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_session_returns_full_object(auth_client):
    """Get session returns full object with all fields present"""
    with allure.step("Create routine with tags and principles"):
        routine_id = create_routine_with_tags_and_principles(
            auth_client,
            "Test Routine",
            tag_names=["fitness", "morning"],
            principle_titles=["Be consistent"]
        )

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        created_session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Test notes",
            "rpe": 7
        })
        session_id = created_session['id']

    with allure.step("Get session by ID"):
        response = auth_client.get(f'/api/sessions/{session_id}')

    with allure.step("Verify all fields present"):
        assert response['id'] == session_id
        assert response['user_id']
        assert response['routine_id'] == routine_id
        assert 'start_time' in response
        assert 'end_time' in response
        assert response['status'] == 'scheduled'
        assert response['notes'] == "Test notes"
        assert response['rpe'] == 7
        assert 'duration_minutes' in response
        assert 'tags' in response
        assert isinstance(response['tags'], list)
        assert 'principles' in response
        assert isinstance(response['principles'], list)
        assert 'created_at' in response
        assert 'updated_at' in response


@allure.feature('Sessions')
@allure.story('Get Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_session_verifies_duration_minutes_computed(auth_client):
    """Get session verifies duration_minutes calculated from start/end times"""
    with allure.step("Create parent routine"):
        routine_id = create_routine_with_tags_and_principles(auth_client, "Test Routine")

    with allure.step("Create session with 90 minute duration"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=90)

        created_session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = created_session['id']

    with allure.step("Get session"):
        response = auth_client.get(f'/api/sessions/{session_id}')

    with allure.step("Verify duration_minutes is 90"):
        assert 'duration_minutes' in response
        assert response['duration_minutes'] == 90, \
            f"Expected duration_minutes to be 90, got {response['duration_minutes']}"


@allure.feature('Sessions')
@allure.story('Get Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_session(auth_client):
    """Get nonexistent session returns 404"""
    with allure.step("Attempt to get nonexistent session"):
        response = auth_client.get('/api/sessions/999999', handle_response=False)

    with allure.step("Verify 404 Not Found"):
        assert response.status_code == 404



@allure.feature('Sessions')
@allure.story('Get Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.get
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_user_session(auth_client, secondary_auth_client):
    """Get another user's session returns 404"""
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

    with allure.step("Primary user attempts to get secondary user's session"):
        response = auth_client.get(f'/api/sessions/{secondary_session_id}',
                                   handle_response=False)

    with allure.step("Verify 404 Not Found"):
        assert response.status_code == 404