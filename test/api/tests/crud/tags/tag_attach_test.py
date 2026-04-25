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
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_to_task(auth_client):
    """Attach tag to task (target_type='task')"""

    with allure.step("Create tag and task"):
        tag = auth_client.post('/api/tags', data={"name": "urgent"})
        task = create_task(auth_client, title="Test task")

    with allure.step("Attach tag to task"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag appears in task's tags field"):
        task_with_tag = auth_client.get(f'/api/tasks/{task["id"]}')
        assert 'tags' in task_with_tag
        tag_ids = [t['id'] for t in task_with_tag['tags']]
        assert tag['id'] in tag_ids, \
            f"Tag {tag['id']} not found in task's tags: {tag_ids}"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_to_project(auth_client):
    """Attach tag to project (target_type='project')"""

    with allure.step("Create tag and project"):
        tag = auth_client.post('/api/tags', data={"name": "work"})
        project = create_project(auth_client, title="Test project")

    with allure.step("Attach tag to project"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "project",
            "target_id": project['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag appears in project's tags field"):
        project_with_tag = auth_client.get(f'/api/projects/{project["id"]}')
        assert 'tags' in project_with_tag
        tag_ids = [t['id'] for t in project_with_tag['tags']]
        assert tag['id'] in tag_ids, \
            f"Tag {tag['id']} not found in project's tags: {tag_ids}"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_to_routine(auth_client):
    """Attach tag to routine (target_type='routine')"""

    with allure.step("Create tag, calendar, and routine"):
        tag = auth_client.post('/api/tags', data={"name": "health"})
        calendar = create_calendar(auth_client, name="Test calendar")
        routine = create_routine(auth_client, title="Test routine", calendar_id=calendar['id'])

    with allure.step("Attach tag to routine"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "routine",
            "target_id": routine['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag appears in routine's tags field"):
        routine_with_tag = auth_client.get(f'/api/routines/{routine["id"]}')
        assert 'tags' in routine_with_tag
        tag_ids = [t['id'] for t in routine_with_tag['tags']]
        assert tag['id'] in tag_ids, \
            f"Tag {tag['id']} not found in routine's tags: {tag_ids}"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_to_session(auth_client):
    """Attach tag to session (target_type='session')"""

    with allure.step("Create tag, calendar, routine, and session"):
        tag = auth_client.post('/api/tags', data={"name": "learning"})
        calendar = create_calendar(auth_client, name="Test calendar")
        routine = create_routine(auth_client, title="Test routine", calendar_id=calendar['id'])
        session = create_session(auth_client, routine['id'])

    with allure.step("Attach tag to session"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "session",
            "target_id": session['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag appears in session's tags field"):
        session_with_tag = auth_client.get(f'/api/sessions/{session["id"]}')
        assert 'tags' in session_with_tag
        tag_ids = [t['id'] for t in session_with_tag['tags']]
        assert tag['id'] in tag_ids, \
            f"Tag {tag['id']} not found in session's tags: {tag_ids}"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_to_calendar(auth_client):
    """Attach tag to calendar (target_type='calendar')"""

    with allure.step("Create tag and calendar"):
        tag = auth_client.post('/api/tags', data={"name": "personal"})
        calendar = create_calendar(auth_client, name="Test calendar")

    with allure.step("Attach tag to calendar"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "calendar",
            "target_id": calendar['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload)

    with allure.step("Verify success response"):
        assert response['success'] is True

    with allure.step("Verify tag appears in calendar's tags field"):
        calendar_with_tag = auth_client.get(f'/api/calendars/{calendar["id"]}')
        assert 'tags' in calendar_with_tag
        tag_ids = [t['id'] for t in calendar_with_tag['tags']]
        assert tag['id'] in tag_ids, \
            f"Tag {tag['id']} not found in calendar's tags: {tag_ids}"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_verifies_idempotent(auth_client):
    """Attach same tag to same entity twice is idempotent"""

    with allure.step("Create tag and task"):
        tag = auth_client.post('/api/tags', data={"name": "test"})
        task = create_task(auth_client, title="Test task")

    with allure.step("Attach tag first time"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        first_response = auth_client.post('/api/tags/attach', data=payload)
        assert first_response['success'] is True

    with allure.step("Attach same tag again"):
        second_response = auth_client.post('/api/tags/attach', data=payload)

    with allure.step("Verify second attachment also succeeds (idempotent)"):
        assert second_response['success'] is True

    with allure.step("Verify tag appears only once in task"):
        task_with_tag = auth_client.get(f'/api/tasks/{task["id"]}')
        assert 'tags' in task_with_tag
        tag_ids = [t['id'] for t in task_with_tag['tags']]
        assert tag_ids.count(tag['id']) == 1, \
            f"Tag {tag['id']} should appear exactly once, found {tag_ids.count(tag['id'])} times"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_without_tag_id(auth_client):
    """Attach tag without tag_id returns 400"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to attach without tag_id"):
        payload = {
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_without_target_type(auth_client):
    """Attach tag without target_type returns 400"""

    with allure.step("Create tag and task"):
        tag = auth_client.post('/api/tags', data={"name": "test"})
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to attach without target_type"):
        payload = {
            "tag_id": tag['id'],
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_without_target_id(auth_client):
    """Attach tag without target_id returns 400"""

    with allure.step("Create tag"):
        tag = auth_client.post('/api/tags', data={"name": "test"})

    with allure.step("Attempt to attach without target_id"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task"
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_with_empty_request_body(auth_client):
    """Attach tag with empty request body returns 400"""

    with allure.step("Attempt to attach with empty body"):
        response = auth_client.post('/api/tags/attach', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_with_invalid_target_type(auth_client):
    """Attach tag with invalid target_type returns 422 with INVALID_TARGET_TYPE"""

    with allure.step("Create tag and task"):
        tag = auth_client.post('/api/tags', data={"name": "test"})
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to attach with invalid target_type"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "invalid_type",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 422 error with INVALID_TARGET_TYPE code"):
        assert response.status_code == 422
        assert 'code' in response
        assert response['code'] == "INVALID_TARGET_TYPE"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_with_nonexistent_tag_id(auth_client):
    """Attach tag with nonexistent tag_id returns 404"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Test task")

    with allure.step("Attempt to attach non-existent tag"):
        payload = {
            "tag_id": 999999,
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_with_nonexistent_target_id(auth_client):
    """Attach tag with nonexistent target_id returns 404"""

    with allure.step("Create tag"):
        tag = auth_client.post('/api/tags', data={"name": "test"})

    with allure.step("Attempt to attach to non-existent task"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": 999999
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_with_another_users_tag(auth_client, secondary_auth_client):
    """Attach another user's tag returns 404"""

    with allure.step("Secondary user creates tag"):
        secondary_tag = secondary_auth_client.post('/api/tags', data={"name": "secondary-tag"})

    with allure.step("Primary user creates task"):
        task = create_task(auth_client, title="Primary user task")

    with allure.step("Primary user attempts to attach secondary user's tag"):
        payload = {
            "tag_id": secondary_tag['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404

    with allure.step("Verify tag does not appear in task's tags field"):
        task = auth_client.get(f'/api/tasks/{task["id"]}')
        assert len(task['tags']) == 0, "Tag should not appear in task's tags"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_tag_with_another_users_target_entity(auth_client, secondary_auth_client):
    """Attach tag to another user's target entity returns 404"""

    with allure.step("Primary user creates tag"):
        tag = auth_client.post('/api/tags', data={"name": "primary-tag"})

    with allure.step("Secondary user creates task"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")

    with allure.step("Primary user attempts to attach tag to secondary user's task"):
        payload = {
            "tag_id": tag['id'],
            "target_type": "task",
            "target_id": secondary_task['id']
        }
        response = auth_client.post('/api/tags/attach', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404

    with allure.step("Verify tag does not appear in task's tags field"):
        task = secondary_auth_client.get(f'/api/tasks/{secondary_task["id"]}')
        assert len(task['tags']) == 0, "Tag should not appear in task's tags"


@allure.feature('Tags')
@allure.story('Attach Tag')
@pytest.mark.tags
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_multiple_tags_to_same_entity(auth_client):
    """Attach multiple tags to same entity"""

    with allure.step("Create 3 tags and a task"):
        tag1 = auth_client.post('/api/tags', data={"name": "urgent"})
        tag2 = auth_client.post('/api/tags', data={"name": "work"})
        tag3 = auth_client.post('/api/tags', data={"name": "important"})
        task = create_task(auth_client, title="Task with multiple tags")

    with allure.step("Attach first tag"):
        payload1 = {
            "tag_id": tag1['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        response1 = auth_client.post('/api/tags/attach', data=payload1)
        assert response1['success'] is True

    with allure.step("Attach second tag"):
        payload2 = {
            "tag_id": tag2['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        response2 = auth_client.post('/api/tags/attach', data=payload2)
        assert response2['success'] is True

    with allure.step("Attach third tag"):
        payload3 = {
            "tag_id": tag3['id'],
            "target_type": "task",
            "target_id": task['id']
        }
        response3 = auth_client.post('/api/tags/attach', data=payload3)
        assert response3['success'] is True

    with allure.step("Verify all 3 tags attached to task"):
        task_with_tags = auth_client.get(f'/api/tasks/{task["id"]}')
        assert 'tags' in task_with_tags
        attached_tag_ids = [t['id'] for t in task_with_tags['tags']]
        assert tag1['id'] in attached_tag_ids
        assert tag2['id'] in attached_tag_ids
        assert tag3['id'] in attached_tag_ids
        assert len(task_with_tags['tags']) == 3