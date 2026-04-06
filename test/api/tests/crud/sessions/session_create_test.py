import pytest
import allure
from datetime import datetime, timedelta


def create_routine(auth_client, routine_title: str,
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
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_all_fields(auth_client):
    """Create session with all fields: start_time, end_time, status, notes, rpe"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    with allure.step("Prepare session data with all fields"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session_data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "completed",
            "notes": "Test session notes",
            "rpe": 8
        }

    with allure.step("Create session"):
        response = auth_client.post(f'/api/routines/{routine_id}/sessions', session_data)

    with allure.step("Verify all fields stored correctly"):
        assert response['id']
        assert response['routine_id'] == routine_id
        assert response['status'] == "completed"
        assert response['notes'] == "Test session notes"
        assert response['rpe'] == 8
        assert response['start_time']
        assert response['end_time']


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_verifies_defaults(auth_client):
    """Create session verifies status='scheduled' when not specified"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    with allure.step("Prepare session data without status"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        session_data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

    with allure.step("Create session"):
        response = auth_client.post(f'/api/routines/{routine_id}/sessions', session_data)

    with allure.step("Verify default status is 'scheduled'"):
        assert response['status'] == 'scheduled'


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_status(auth_client):
    """Create session with status completed"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    statuses = ["completed", "cancelled", "skipped"]
    for status in statuses:
        with allure.step(f"Create session with status={status}"):
            now = datetime.utcnow()
            start_time = now + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)

            response = auth_client.post(f'/api/routines/{routine_id}/sessions', {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "status": status
            })

        with allure.step("Verify status is set correctly"):
            assert response['status'] == status



@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_notes_and_rpe(auth_client):
    """Create session with notes and rpe"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    with allure.step("Create session with notes and rpe"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Great workout session",
            "rpe": 9
        })

    with allure.step("Verify notes and rpe stored correctly"):
        assert response['notes'] == "Great workout session"
        assert response['rpe'] == 9


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_inherit_tags_true(auth_client):
    """Create session with inherit_tags=true (default) verifies tags inherited"""
    with allure.step("Create routine with tags"):
        routine_id = create_routine(
            auth_client,
            "Routine with Tags",
            tag_names=["fitness", "morning"]
        )

    with allure.step("Create session with default inherit_tags=true"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })

    with allure.step("Verify tags inherited from routine"):
        assert 'tags' in response
        tag_names = [tag['name'] for tag in response['tags']]
        assert 'fitness' in tag_names
        assert 'morning' in tag_names


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_inherit_tags_false(auth_client):
    """Create session with inherit_tags=false verifies session has no tags"""
    with allure.step("Create routine with tags"):
        routine_id = create_routine(
            auth_client,
            "Routine with Tags",
            tag_names=["fitness", "morning"]
        )

    with allure.step("Create session with inherit_tags=false"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(
            f'/api/routines/{routine_id}/sessions',
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            params={"inherit_tags": False}
        )

    with allure.step("Verify session has no tags"):
        assert 'tags' in response
        assert len(response['tags']) == 0


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_inherit_principles_true(auth_client):
    """Create session with inherit_principles=true (default) verifies principles inherited"""
    with allure.step("Create routine with principles"):
        routine_id = create_routine(
            auth_client,
            "Routine with Principles",
            principle_titles=["Be consistent", "Prioritize health"]
        )

    with allure.step("Create session with default inherit_principles=true"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })

    with allure.step("Verify principles inherited from routine"):
        assert 'principles' in response
        principle_titles = [p['title'] for p in response['principles']]
        assert 'Be consistent' in principle_titles
        assert 'Prioritize health' in principle_titles


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_inherit_principles_false(auth_client):
    """Create session with inherit_principles=false verifies session has no principles"""
    with allure.step("Create routine with principles"):
        routine_id = create_routine(
            auth_client,
            "Routine with Principles",
            principle_titles=["Be consistent", "Prioritize health"]
        )

    with allure.step("Create session with inherit_principles=false"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(
            f'/api/routines/{routine_id}/sessions',
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            params={"inherit_principles": False}
        )

    with allure.step("Verify session has no principles"): #lol roasted
        assert 'principles' in response
        assert len(response['principles']) == 0


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_both_inheritance_flags_false(auth_client):
    """Create session with both inheritance flags false verifies session has no tags or principles"""
    with allure.step("Create routine with tags and principles"):
        routine_id = create_routine(
            auth_client,
            "Routine with Tags and Principles",
            tag_names=["fitness"],
            principle_titles=["Be consistent"]
        )

    with allure.step("Create session with both inheritance flags false"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(
            f'/api/routines/{routine_id}/sessions',
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            params={"inherit_tags": False, "inherit_principles": False}
        )

    with allure.step("Verify session has no tags or principles"):
        assert 'tags' in response
        assert len(response['tags']) == 0
        assert 'principles' in response
        assert len(response['principles']) == 0


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_verifies_commitment_auto_created(auth_client):
    """Create session verifies hard commitment exists for session"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    with allure.step("Create session"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        session = auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        session_id = session['id']

    with allure.step("Verify commitment exists for session"):
        # Query commitments to find the auto-created one
        commitments_response = auth_client.get('/api/commitments')
        commitments = commitments_response.json

        session_commitments = [
            c for c in commitments
            if c.get('target_type') == 'session' and c.get('target_id') == session_id
        ]

        assert len(session_commitments) == 1, "Expected exactly one commitment for session"
        commitment = session_commitments[0]
        assert commitment['target_type'] == 'session'
        assert commitment['target_id'] == session_id


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_without_start_time(auth_client):
    """Create session without start_time returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    with allure.step("Attempt to create session without start_time"):
        now = datetime.utcnow()
        end_time = now + timedelta(hours=2)

        response = auth_client.post(
            f'/api/routines/{routine_id}/sessions',
            {"end_time": end_time.isoformat()},
            handle_response=False
        )

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_without_end_time(auth_client):
    """Create session without end_time returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    with allure.step("Attempt to create session without end_time"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)

        response = auth_client.post(
            f'/api/routines/{routine_id}/sessions',
            {"start_time": start_time.isoformat()},
            handle_response=False
        )

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_with_empty_request_body(auth_client):
    """Create session with empty request body returns 400 error"""
    with allure.step("Create parent routine"):
        routine_id = create_routine(auth_client, "Test Routine")

    with allure.step("Attempt to create session with empty body"):
        response = auth_client.post(
            f'/api/routines/{routine_id}/sessions',
            {},
            handle_response=False
        )

    with allure.step("Verify 400 Bad Request"):
        assert response.status_code == 400


@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_for_nonexistent_routine(auth_client):
    """Create session for nonexistent routine returns 400 or 404 error"""
    with allure.step("Attempt to create session for nonexistent routine"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(
            '/api/routines/999999/sessions',
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == "Routine with ID 999999 not found"

@allure.feature('Sessions')
@allure.story('Create Session')
@pytest.mark.sessions
@pytest.mark.crud
@pytest.mark.create
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_create_session_for_another_user_routine(auth_client, secondary_auth_client):
    """Create session for another user's routine returns 404 error"""
    with allure.step("Secondary user creates routine"):
        secondary_routine = secondary_auth_client.post('/api/routines', {
            "title": "Secondary User Routine"
        })
        secondary_routine_id = secondary_routine['id']

    with allure.step("Primary user attempts to create session for secondary user's routine"):
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        response = auth_client.post(
            f'/api/routines/{secondary_routine_id}/sessions',
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            handle_response=False
        )

    with allure.step("Verify 404 Not Found"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == f"Routine with ID {secondary_routine_id} not found"
