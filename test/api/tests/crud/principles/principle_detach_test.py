import pytest
import allure
from utils.data_factories.entity_factory import (
    create_task,
    create_project,
    create_calendar,
    create_routine,
    create_session
)


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_from_task(auth_client):
    """Attach then detach, verify removal"""

    with allure.step("Create principle and task"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        task = create_task(auth_client, title="Task for detach test")
        task_id = task['id']

    with allure.step("Attach principle to task"):
        auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": task_id
        })

    with allure.step("Verify principle attached"):
        task_before = auth_client.get(f'/api/tasks/{task_id}')
        task_principle_ids = [p['id'] for p in task_before.get('principles', [])]
        assert principle_id in task_principle_ids

    with allure.step("Detach principle from task"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": task_id
        })

    with allure.step("Verify detachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle removed from task"):
        task_after = auth_client.get(f'/api/tasks/{task_id}')
        task_principle_ids_after = [p['id'] for p in task_after.get('principles', [])]
        assert principle_id not in task_principle_ids_after


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_from_project(auth_client):
    """Attach then detach, verify removal"""

    with allure.step("Create principle and project"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        project = create_project(auth_client, title="Project for detach test")
        project_id = project['id']

    with allure.step("Attach principle to project"):
        auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "project",
            "target_id": project_id
        })

    with allure.step("Verify principle attached"):
        project_before = auth_client.get(f'/api/projects/{project_id}')
        project_principle_ids = [p['id'] for p in project_before.get('principles', [])]
        assert principle_id in project_principle_ids

    with allure.step("Detach principle from project"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "project",
            "target_id": project_id
        })

    with allure.step("Verify detachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle removed from project"):
        project_after = auth_client.get(f'/api/projects/{project_id}')
        project_principle_ids_after = [p['id'] for p in project_after.get('principles', [])]
        assert principle_id not in project_principle_ids_after


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_from_calendar(auth_client):
    """Attach then detach, verify removal"""

    with allure.step("Create principle and calendar"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        calendar = create_calendar(auth_client, name="Calendar for detach test")
        calendar_id = calendar['id']

    with allure.step("Attach principle to calendar"):
        auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "calendar",
            "target_id": calendar_id
        })

    with allure.step("Verify principle attached"):
        calendar_before = auth_client.get(f'/api/calendars/{calendar_id}')
        calendar_principle_ids = [p['id'] for p in calendar_before.get('principles', [])]
        assert principle_id in calendar_principle_ids

    with allure.step("Detach principle from calendar"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "calendar",
            "target_id": calendar_id
        })

    with allure.step("Verify detachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle removed from calendar"):
        calendar_after = auth_client.get(f'/api/calendars/{calendar_id}')
        calendar_principle_ids_after = [p['id'] for p in calendar_after.get('principles', [])]
        assert principle_id not in calendar_principle_ids_after


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_from_routine(auth_client):
    """Attach then detach, verify removal"""

    with allure.step("Create principle and routine"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        routine = create_routine(auth_client, title="Routine for detach test")
        routine_id = routine['id']

    with allure.step("Attach principle to routine"):
        auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "routine",
            "target_id": routine_id
        })

    with allure.step("Verify principle attached"):
        routine_before = auth_client.get(f'/api/routines/{routine_id}')
        routine_principle_ids = [p['id'] for p in routine_before.get('principles', [])]
        assert principle_id in routine_principle_ids

    with allure.step("Detach principle from routine"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "routine",
            "target_id": routine_id
        })

    with allure.step("Verify detachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle removed from routine"):
        routine_after = auth_client.get(f'/api/routines/{routine_id}')
        routine_principle_ids_after = [p['id'] for p in routine_after.get('principles', [])]
        assert principle_id not in routine_principle_ids_after


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_from_session(auth_client):
    """Attach then detach, verify removal"""

    with allure.step("Create principle, routine, and session"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        routine = create_routine(auth_client, title="Routine for session")
        routine_id = routine['id']
        session = create_session(auth_client, routine_id=routine_id)
        session_id = session['id']

    with allure.step("Attach principle to session"):
        auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "session",
            "target_id": session_id
        })

    with allure.step("Verify principle attached"):
        session_before = auth_client.get(f'/api/sessions/{session_id}')
        session_principle_ids = [p['id'] for p in session_before.get('principles', [])]
        assert principle_id in session_principle_ids

    with allure.step("Detach principle from session"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "session",
            "target_id": session_id
        })

    with allure.step("Verify detachment successful"):
        assert response['success'] is True

    with allure.step("Verify principle removed from session"):
        session_after = auth_client.get(f'/api/sessions/{session_id}')
        session_principle_ids_after = [p['id'] for p in session_after.get('principles', [])]
        assert principle_id not in session_principle_ids_after


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_verifies_not_idempotent(auth_client):
    """Detach non-attached principle, verify error"""

    with allure.step("Create principle and task"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        task = create_task(auth_client, title="Task for non-idempotent test")
        task_id = task['id']

    with allure.step("Attempt to detach principle that was never attached"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify error (detach is not idempotent)"):
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404 for detaching unattached principle, got {response.status_code}"


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_without_principle_id(auth_client):
    """Verify 400 error when principle_id missing"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for missing principle_id")
        task_id = task['id']

    with allure.step("Attempt to detach without principle_id"):
        response = auth_client.post('/api/principles/detach', data={
            "target_type": "task",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_without_target_type(auth_client):
    """Verify 400 error when target_type missing"""

    with allure.step("Create principle and task"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        task = create_task(auth_client, title="Task for missing target_type")
        task_id = task['id']

    with allure.step("Attempt to detach without target_type"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_without_target_id(auth_client):
    """Verify 400 error when target_id missing"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']

    with allure.step("Attempt to detach without target_id"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "task"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_with_empty_request_body(auth_client):
    """Verify 400 error with empty request body"""

    with allure.step("Attempt to detach with empty body"):
        response = auth_client.post('/api/principles/detach', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_with_invalid_target_type(auth_client):
    """Verify 422 error with code 'INVALID_TARGET_TYPE'"""

    with allure.step("Create principle and task"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']
        task = create_task(auth_client, title="Task for invalid target type")
        task_id = task['id']

    with allure.step("Attempt to detach with invalid target_type"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "invalid_type",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 422 error with INVALID_TARGET_TYPE code"):
        assert response.status_code == 422
        assert 'code' in response
        assert response['code'] == "INVALID_TARGET_TYPE"


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_with_nonexistent_principle_id(auth_client):
    """Verify 404 error with non-existent principle"""

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for nonexistent principle")
        task_id = task['id']

    with allure.step("Attempt to detach non-existent principle"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": 999999,
            "target_type": "task",
            "target_id": task_id
        }, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_with_nonexistent_target_id(auth_client):
    """Verify 404 error with non-existent target entity"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = principle['id']

    with allure.step("Attempt to detach from non-existent task"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": 999999
        }, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Detach Principle')
@pytest.mark.principles
@pytest.mark.detach
@allure.severity(allure.severity_level.NORMAL)
def test_detach_principle_from_another_users_target_entity(auth_client, secondary_auth_client):
    """Verify 404 when detaching from another user's target entity"""

    with allure.step("Primary user creates principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Primary user principle"
        })
        principle_id = principle['id']

    with allure.step("Secondary user creates task"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_task_id = secondary_task['id']

    with allure.step("Primary user attempts to detach from secondary user's task"):
        response = auth_client.post('/api/principles/detach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": secondary_task_id
        }, handle_response=False)

    with allure.step("Verify 404 error (not authorized to modify other user's entity)"):
        assert response.status_code == 404