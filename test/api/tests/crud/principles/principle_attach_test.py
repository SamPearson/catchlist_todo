
import pytest
import allure
from test_utils.data_factories.entity_factory import (
    create_task,
    create_project,
    create_calendar,
    create_routine,
    create_session
)


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_to_task(auth_client):
    """Verify target_type='task' works"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Be dependable"
        })
        principle_id = principle['id']

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for principle")
        task_id = task['id']

    with allure.step("Attach principle to task"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": task_id
        })

    with allure.step("Verify attachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle appears on task"):
        task_check = auth_client.get(f'/api/tasks/{task_id}')
        task_principle_ids = [p['id'] for p in task_check.get('principles', [])]
        assert principle_id in task_principle_ids


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_to_project(auth_client):
    """Verify target_type='project' works"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Continuous learning"
        })
        principle_id = principle['id']

    with allure.step("Create project"):
        project = create_project(auth_client, title="Project for principle")
        project_id = project['id']

    with allure.step("Attach principle to project"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "project",
            "target_id": project_id
        })

    with allure.step("Verify attachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle appears on project"):
        project_check = auth_client.get(f'/api/projects/{project_id}')
        project_principle_ids = [p['id'] for p in project_check.get('principles', [])]
        assert principle_id in project_principle_ids


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_to_calendar(auth_client):
    """Verify target_type='calendar' works"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Prioritize health"
        })
        principle_id = principle['id']

    with allure.step("Create calendar"):
        calendar = create_calendar(auth_client, name="Calendar for principle")
        calendar_id = calendar['id']

    with allure.step("Attach principle to calendar"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "calendar",
            "target_id": calendar_id
        })

    with allure.step("Verify attachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle appears on calendar"):
        calendar_check = auth_client.get(f'/api/calendars/{calendar_id}')
        calendar_principle_ids = [p['id'] for p in calendar_check.get('principles', [])]
        assert principle_id in calendar_principle_ids


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_to_routine(auth_client):
    """Verify target_type='routine' works"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Practice consistency"
        })
        principle_id = principle['id']

    with allure.step("Create routine"):
        routine = create_routine(auth_client, title="Routine for principle")
        routine_id = routine['id']

    with allure.step("Attach principle to routine"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "routine",
            "target_id": routine_id
        })

    with allure.step("Verify attachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle appears on routine"):
        routine_check = auth_client.get(f'/api/routines/{routine_id}')
        routine_principle_ids = [p['id'] for p in routine_check.get('principles', [])]
        assert principle_id in routine_principle_ids


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_to_session(auth_client):
    """Verify target_type='session' works"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Embrace growth"
        })
        principle_id = principle['id']

    with allure.step("Create routine and session"):
        routine = create_routine(auth_client, title="Routine for session")
        routine_id = routine['id']
        session = create_session(auth_client, routine_id=routine_id)
        session_id = session['id']

    with allure.step("Attach principle to session"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "session",
            "target_id": session_id
        })

    with allure.step("Verify attachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle appears on session"):
        session_check = auth_client.get(f'/api/sessions/{session_id}')
        session_principle_ids = [p['id'] for p in session_check.get('principles', [])]
        assert principle_id in session_principle_ids


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_verifies_idempotent(auth_client):
    """Attach same principle to same entity twice, verify success both times"""

    with allure.step("Create principle and task"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        task = create_task(auth_client, title="Task for idempotency test")
        task_id = task['id']

    with allure.step("Attach principle to task (first time)"):
        first_attach = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": task_id
        })
        assert first_attach['success'] is True

    with allure.step("Attach same principle to same task (second time)"):
        second_attach = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": task_id
        })
        assert second_attach['success'] is True

    with allure.step("Verify principle appears only once on task"):
        task_check = auth_client.get(f'/api/tasks/{task_id}')
        task_principle_ids = [p['id'] for p in task_check.get('principles', [])]
        principle_count = task_principle_ids.count(principle_id)
        assert principle_count == 1, f"Expected principle to appear once, but appeared {principle_count} times"


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_without_principle_id(auth_client):
    """Verify 400 error when principle_id missing"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task without principle_id")
        task_id = task['id']

    with allure.step("Attempt to attach without principle_id"):
        response = auth_client.post('/api/principles/attach', data={
            "target_type": "task",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_without_target_type(auth_client):
    """Verify 400 error when target_type missing"""

    with allure.step("Create principle and task"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        task = create_task(auth_client, title="Task without target_type")
        task_id = task['id']

    with allure.step("Attempt to attach without target_type"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_without_target_id(auth_client):
    """Verify 400 error when target_id missing"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']

    with allure.step("Attempt to attach without target_id"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_with_empty_request_body(auth_client):
    """Verify 400 error with empty request body"""

    with allure.step("Attempt to attach with empty body"):
        response = auth_client.post('/api/principles/attach', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_with_invalid_target_type(auth_client):
    """Verify 422 error with code 'INVALID_TARGET_TYPE'"""

    with allure.step("Create principle and task"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        task = create_task(auth_client, title="Task for invalid target type")
        task_id = task['id']

    with allure.step("Attempt to attach with invalid target_type"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "invalid_type",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 422 error with INVALID_TARGET_TYPE code"):
        assert response.status_code == 422
        assert 'code' in response
        assert response['code'] == "INVALID_TARGET_TYPE"


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_to_report_target(auth_client):
    """Verify 422 error (report not in principled entities list)"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']

    with allure.step("Attempt to attach principle to report"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "report",
            "target_id": 1
        }, handle_response=False)

    with allure.step("Verify 422 error (report not supported for principles)"):
        assert response.status_code == 422
        assert 'code' in response
        assert response['code'] == "INVALID_TARGET_TYPE"


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_with_nonexistent_principle_id(auth_client):
    """Verify 404 error with non-existent principle"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for nonexistent principle")
        task_id = task['id']

    with allure.step("Attempt to attach non-existent principle"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": 999999,
            "target_type": "task",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_with_nonexistent_target_id(auth_client):
    """Verify 404 error with non-existent target entity"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']

    with allure.step("Attempt to attach to non-existent task"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": 999999
        }, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_with_another_users_principle(auth_client, secondary_auth_client):
    """Verify 404 error when using another user's principle"""

    with allure.step("Secondary user creates principle"):
        secondary_principle = secondary_auth_client.post('/api/principles', data={
            "title": "Secondary user principle"
        })
        secondary_principle_id = secondary_principle['id']

    with allure.step("Primary user creates task"):
        task = create_task(auth_client, title="Primary user task")
        task_id = task['id']

    with allure.step("Primary user attempts to attach secondary user's principle"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": secondary_principle_id,
            "target_type": "task",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 404 error (not authorized to use other user's principle)"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_principle_with_another_users_target_entity(auth_client, secondary_auth_client):
    """Verify 404 error when attaching to another user's target entity"""

    with allure.step("Primary user creates principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Primary user principle"
        })
        principle_id = principle['id']

    with allure.step("Secondary user creates task"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_task_id = secondary_task['id']

    with allure.step("Primary user attempts to attach to secondary user's task"):
        response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": secondary_task_id
        }, handle_response=False)

    with allure.step("Verify 404 error (not authorized to modify other user's entity)"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Attach Principle')
@pytest.mark.principles
@pytest.mark.attach
@allure.severity(allure.severity_level.NORMAL)
def test_attach_multiple_principles_to_same_entity(auth_client):
    """Verify multiple attachments work"""

    with allure.step("Create three principles"):
        principle1 = auth_client.post('/api/principles', data={
            "title": "Principle 1"
        })
        principle2 = auth_client.post('/api/principles', data={
            "title": "Principle 2"
        })
        principle3 = auth_client.post('/api/principles', data={
            "title": "Principle 3"
        })
        principle_ids = [principle1['id'], principle2['id'], principle3['id']]

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task with multiple principles")
        task_id = task['id']

    with allure.step("Attach all three principles to task"):
        for principle_id in principle_ids:
            response = auth_client.post('/api/principles/attach', data={
                "principle_id": principle_id,
                "target_type": "task",
                "target_id": task_id
            })
            assert response['success'] is True

    with allure.step("Verify all three principles appear on task"):
        task_check = auth_client.get(f'/api/tasks/{task_id}')
        task_principle_ids = [p['id'] for p in task_check.get('principles', [])]
        for principle_id in principle_ids:
            assert principle_id in task_principle_ids, \
                f"Principle {principle_id} not found in task's principles"
        assert len(task_principle_ids) >= 3