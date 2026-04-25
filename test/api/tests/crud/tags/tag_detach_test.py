import pytest
import allure
from test_utils.data_factories.entity_factory import (
    create_task,
    create_project,
    create_routine,
    create_session,
    create_calendar
)


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_from_task(auth_client):
    """Detach tag from task (attach then detach, verify removal)"""

    with allure.step("Create tag and task"):
        tag = auth_client.post('/api/tags', data={"name": "urgent"})
        task = create_task(auth_client, title="Test task")

    with allure.step("Attach tag to task"):
        attach_payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        auth_client.post('/api/tags/attach', data=attach_payload)

    with allure.step("Verify tag is attached"):
        task_with_tag = auth_client.get(f'/api/tasks/{task["id"]}')
        assert 'tags' in task_with_tag
        tag_ids = [t['id'] for t in task_with_tag['tags']]
        assert tag['id'] in tag_ids

    with allure.step("Detach tag from task"):
        detach_payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/detach', data=detach_payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag removed from task"):
        task_after_detach = auth_client.get(f'/api/tasks/{task["id"]}')
        assert 'tags' in task_after_detach
        if task_after_detach['tags']:
            remaining_tag_ids = [t['id'] for t in task_after_detach['tags']]
            assert tag['id'] not in remaining_tag_ids, \
                f"Tag {tag['id']} should be removed but still found in tags: {remaining_tag_ids}"
        else:
            # Tags list is empty - tag was removed
            assert len(task_after_detach['tags']) == 0


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_from_project(auth_client):
    """Detach tag from project (attach then detach, verify removal)"""

    with allure.step("Create tag and project"):
        tag = auth_client.post('/api/tags', data={"name": "work"})
        project = create_project(auth_client, title="Test project")

    with allure.step("Attach tag to project"):
        attach_payload = {
            "tag_id": tag['id'],
            "target_type": "project",
            "target_id": project['id']
        }
        auth_client.post('/api/tags/attach', data=attach_payload)

    with allure.step("Verify tag is attached"):
        project_with_tag = auth_client.get(f'/api/projects/{project["id"]}')
        assert 'tags' in project_with_tag
        tag_ids = [t['id'] for t in project_with_tag['tags']]
        assert tag['id'] in tag_ids

    with allure.step("Detach tag from project"):
        detach_payload = {
            "tag_id": tag['id'],
            "target_type": "project",
            "target_id": project['id']
        }
        response = auth_client.post('/api/tags/detach', data=detach_payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag removed from project"):
        project_after_detach = auth_client.get(f'/api/projects/{project["id"]}')
        assert 'tags' in project_after_detach
        if project_after_detach['tags']:
            remaining_tag_ids = [t['id'] for t in project_after_detach['tags']]
            assert tag['id'] not in remaining_tag_ids, \
                f"Tag {tag['id']} should be removed but still found in tags: {remaining_tag_ids}"
        else:
            assert len(project_after_detach['tags']) == 0


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_from_routine(auth_client):
    """Detach tag from routine (attach then detach, verify removal)"""

    with allure.step("Create tag, calendar, and routine"):
        tag = auth_client.post('/api/tags', data={"name": "health"})
        calendar = create_calendar(auth_client, name="Test calendar")
        routine = create_routine(auth_client, title="Test routine", calendar_id=calendar['id'])

    with allure.step("Attach tag to routine"):
        attach_payload = {
            "tag_id": tag['id'],
            "target_type": "routine",
            "target_id": routine['id']
        }
        auth_client.post('/api/tags/attach', data=attach_payload)

    with allure.step("Verify tag is attached"):
        routine_with_tag = auth_client.get(f'/api/routines/{routine["id"]}')
        assert 'tags' in routine_with_tag
        tag_ids = [t['id'] for t in routine_with_tag['tags']]
        assert tag['id'] in tag_ids

    with allure.step("Detach tag from routine"):
        detach_payload = {
            "tag_id": tag['id'],
            "target_type": "routine",
            "target_id": routine['id']
        }
        response = auth_client.post('/api/tags/detach', data=detach_payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag removed from routine"):
        routine_after_detach = auth_client.get(f'/api/routines/{routine["id"]}')
        assert 'tags' in routine_after_detach
        if routine_after_detach['tags']:
            remaining_tag_ids = [t['id'] for t in routine_after_detach['tags']]
            assert tag['id'] not in remaining_tag_ids, \
                f"Tag {tag['id']} should be removed but still found in tags: {remaining_tag_ids}"
        else:
            assert len(routine_after_detach['tags']) == 0


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_from_session(auth_client):
    """Detach tag from session (attach then detach, verify removal)"""

    with allure.step("Create tag, calendar, routine, and session"):
        tag = auth_client.post('/api/tags', data={"name": "learning"})
        calendar = create_calendar(auth_client, name="Test calendar")
        routine = create_routine(auth_client, title="Test routine", calendar_id=calendar['id'])
        session = create_session(auth_client, routine['id'])

    with allure.step("Attach tag to session"):
        attach_payload = {
            "tag_id": tag['id'],
            "target_type": "session",
            "target_id": session['id']
        }
        auth_client.post('/api/tags/attach', data=attach_payload)

    with allure.step("Verify tag is attached"):
        session_with_tag = auth_client.get(f'/api/sessions/{session["id"]}')
        assert 'tags' in session_with_tag
        tag_ids = [t['id'] for t in session_with_tag['tags']]
        assert tag['id'] in tag_ids

    with allure.step("Detach tag from session"):
        detach_payload = {
            "tag_id": tag['id'],
            "target_type": "session",
            "target_id": session['id']
        }
        response = auth_client.post('/api/tags/detach', data=detach_payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag removed from session"):
        session_after_detach = auth_client.get(f'/api/sessions/{session["id"]}')
        assert 'tags' in session_after_detach
        if session_after_detach['tags']:
            remaining_tag_ids = [t['id'] for t in session_after_detach['tags']]
            assert tag['id'] not in remaining_tag_ids, \
                f"Tag {tag['id']} should be removed but still found in tags: {remaining_tag_ids}"
        else:
            assert len(session_after_detach['tags']) == 0


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_from_calendar(auth_client):
    """Detach tag from calendar (attach then detach, verify removal)"""

    with allure.step("Create tag and calendar"):
        tag = auth_client.post('/api/tags', data={"name": "personal"})
        calendar = create_calendar(auth_client, name="Test calendar")

    with allure.step("Attach tag to calendar"):
        attach_payload = {
            "tag_id": tag['id'],
            "target_type": "calendar",
            "target_id": calendar['id']
        }
        auth_client.post('/api/tags/attach', data=attach_payload)

    with allure.step("Verify tag is attached"):
        calendar_with_tag = auth_client.get(f'/api/calendars/{calendar["id"]}')
        assert 'tags' in calendar_with_tag
        tag_ids = [t['id'] for t in calendar_with_tag['tags']]
        assert tag['id'] in tag_ids

    with allure.step("Detach tag from calendar"):
        detach_payload = {
            "tag_id": tag['id'],
            "target_type": "calendar",
            "target_id": calendar['id']
        }
        response = auth_client.post('/api/tags/detach', data=detach_payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag removed from calendar"):
        calendar_after_detach = auth_client.get(f'/api/calendars/{calendar["id"]}')
        assert 'tags' in calendar_after_detach
        if calendar_after_detach['tags']:
            remaining_tag_ids = [t['id'] for t in calendar_after_detach['tags']]
            assert tag['id'] not in remaining_tag_ids, \
                f"Tag {tag['id']} should be removed but still found in tags: {remaining_tag_ids}"
        else:
            assert len(calendar_after_detach['tags']) == 0


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_unattached_tag(auth_client):
    """Detach non-attached tag throws an error"""

    with allure.step("Create tag and task"):
        tag_name = 'test'
        tag = auth_client.post('/api/tags', data={"name": tag_name})
        task = create_task(auth_client, title="Test task")

    with allure.step("Detach tag that was never attached"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify error message"):
        assert response.status_code == 400
        assert 'error' in response
        assert f"Tag '{tag_name}' is not attached" in response['error']

    with allure.step("Verify task has empty tags list"):
        task_after_detach = auth_client.get(f'/api/tasks/{task["id"]}')
        assert 'tags' in task_after_detach
        assert len(task_after_detach['tags']) == 0, \
            f"Expected empty tags list, found: {task_after_detach['tags']}"


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_without_tag_id(auth_client):
    """Detach tag without tag_id returns 400"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to detach without tag_id"):
        payload = {
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_without_target_type(auth_client):
    """Detach tag without target_type returns 400"""

    with allure.step("Create tag and task"):
        tag = auth_client.post('/api/tags', data={"name": "test"})
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to detach without target_type"):
        payload = {
            "tag_id": tag['id'],
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_without_target_id(auth_client):
    """Detach tag without target_id returns 400"""

    with allure.step("Create tag"):
        tag = auth_client.post('/api/tags', data={"name": "test"})

    with allure.step("Attempt to detach without target_id"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task"
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_with_empty_request_body(auth_client):
    """Detach tag with empty request body returns 400"""

    with allure.step("Attempt to detach with empty body"):
        response = auth_client.post('/api/tags/detach', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_with_invalid_target_type(auth_client):
    """Detach tag with invalid target_type returns 422 with INVALID_TARGET_TYPE"""

    with allure.step("Create tag and task"):
        tag = auth_client.post('/api/tags', data={"name": "test"})
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to detach with invalid target_type"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "invalid_type",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify 422 error with INVALID_TARGET_TYPE code"):
        assert response.status_code == 422
        assert 'code' in response
        assert response['code'] == "INVALID_TARGET_TYPE"


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_with_nonexistent_tag_id(auth_client):
    """Detach tag with nonexistent tag_id returns 404"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to detach non-existent tag"):
        payload = {
            "tag_id": 999999,
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_with_nonexistent_target_id(auth_client):
    """Detach tag with nonexistent target_id returns 404"""

    with allure.step("Create tag"):
        tag = auth_client.post('/api/tags', data={"name": "test"})

    with allure.step("Attempt to detach from non-existent task"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": 999999
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Tags')
@allure.story('Detach Tag')
@pytest.mark.tags
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_tag_from_another_users_target_entity(auth_client, secondary_auth_client):
    """Detach tag from another user's target entity returns 404"""

    with allure.step("Primary user creates tag"):
        tag = auth_client.post('/api/tags', data={"name": "primary-tag"})

    with allure.step("Secondary user creates task"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")

    with allure.step("Primary user attempts to detach tag from secondary user's task"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": secondary_task['id']
        }
        response = auth_client.post('/api/tags/detach', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404