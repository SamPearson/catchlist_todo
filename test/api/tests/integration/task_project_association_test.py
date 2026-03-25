
import pytest
import allure


# ===== Attach to Project Tests =====

@allure.feature('Tasks')
@allure.story('Project Association - Attach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_attach_standalone_task_to_project(auth_client):
    """Attach standalone task to project sets project_id"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Create standalone task"):
        task = auth_client.post('/api/tasks', {
            "title": "Standalone task"
        })
        task_id = task['id']
        assert task['project_id'] is None

    with allure.step("Attach task to project"):
        attached = auth_client.patch(f'/api/tasks/{task_id}/attach/{project_id}')

    with allure.step("Verify task is now attached to project"):
        assert attached['id'] == task_id
        assert attached['project_id'] == project_id
        assert attached['title'] == task['title']


@allure.feature('Tasks')
@allure.story('Project Association - Attach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_attach_task_already_attached_to_project_a_to_project_b(auth_client):
    """Attach task already attached to project A to project B moves it to project B"""
    with allure.step("Create two projects"):
        project_a = auth_client.post('/api/projects', {
            "title": "Project A"
        })
        project_a_id = project_a['id']

        project_b = auth_client.post('/api/projects', {
            "title": "Project B"
        })
        project_b_id = project_b['id']

    with allure.step("Create task attached to project A"):
        task = auth_client.post('/api/tasks', {
            "title": "Task to move",
            "project_id": project_a_id
        })
        task_id = task['id']
        assert task['project_id'] == project_a_id

    with allure.step("Attach task to project B"):
        attached = auth_client.patch(f'/api/tasks/{task_id}/attach/{project_b_id}')

    with allure.step("Verify task is now attached to project B"):
        assert attached['id'] == task_id
        assert attached['project_id'] == project_b_id


@allure.feature('Tasks')
@allure.story('Project Association - Attach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_attach_task_to_nonexistent_project(auth_client):
    """Attach task to nonexistent project returns 400 error"""
    with allure.step("Create standalone task"):
        task = auth_client.post('/api/tasks', {
            "title": "Standalone task"
        })
        task_id = task['id']

    with allure.step("Attempt to attach task to nonexistent project"):
        response = auth_client.patch(f'/api/tasks/{task_id}/attach/999999',
                                     handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Project Association - Attach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_attach_task_to_another_users_project(auth_client, secondary_auth_client):
    """Attach task to another user's project returns 400 error"""
    with allure.step("Create project as second user"):
        user2_project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        user2_project_id = user2_project['id']

    with allure.step("Create task as first user"):
        user1_task = auth_client.post('/api/tasks', {
            "title": "User 1 task"
        })
        user1_task_id = user1_task['id']

    with allure.step("Attempt to attach first user's task to second user's project"):
        response = auth_client.patch(
            f'/api/tasks/{user1_task_id}/attach/{user2_project_id}',
            handle_response=False
        )

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Project Association - Attach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_attach_nonexistent_task(auth_client):
    """Attach nonexistent task returns 404"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Attempt to attach nonexistent task"):
        response = auth_client.patch(f'/api/tasks/999999/attach/{project_id}',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Project Association - Attach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_attach_another_users_task(auth_client, secondary_auth_client):
    """Attach another user's task returns 404"""
    with allure.step("Create project as first user"):
        user1_project = auth_client.post('/api/projects', {
            "title": "User 1 project"
        })
        user1_project_id = user1_project['id']

    with allure.step("Create task as second user"):
        user2_task = secondary_auth_client.post('/api/tasks', {
            "title": "User 2 task"
        })
        user2_task_id = user2_task['id']

    with allure.step("Attempt to attach second user's task as first user"):
        response = auth_client.patch(
            f'/api/tasks/{user2_task_id}/attach/{user1_project_id}',
            handle_response=False
        )

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


# ===== Detach from Project Tests =====

@allure.feature('Tasks')
@allure.story('Project Association - Detach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_detach_task_from_project(auth_client):
    """Detach task from project clears project_id"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Create task attached to project"):
        task = auth_client.post('/api/tasks', {
            "title": "Subtask",
            "project_id": project_id
        })
        task_id = task['id']
        assert task['project_id'] == project_id

    with allure.step("Detach task from project"):
        detached = auth_client.patch(f'/api/tasks/{task_id}/detach')

    with allure.step("Verify task is now standalone"):
        assert detached['id'] == task_id
        assert detached['project_id'] is None
        assert detached['title'] == task['title']


@allure.feature('Tasks')
@allure.story('Project Association - Detach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_detach_already_standalone_task(auth_client):
    """Detach already standalone task is idempotent (no error)"""
    with allure.step("Create standalone task"):
        task = auth_client.post('/api/tasks', {
            "title": "Standalone task"
        })
        task_id = task['id']
        assert task['project_id'] is None

    with allure.step("Detach task (already standalone)"):
        detached = auth_client.patch(f'/api/tasks/{task_id}/detach')

    with allure.step("Verify task remains standalone with no error"):
        assert detached['id'] == task_id
        assert detached['project_id'] is None


@allure.feature('Tasks')
@allure.story('Project Association - Detach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_detach_nonexistent_task(auth_client):
    """Detach nonexistent task returns 404"""
    with allure.step("Attempt to detach nonexistent task"):
        response = auth_client.patch('/api/tasks/999999/detach',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Project Association - Detach')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_detach_another_users_task(auth_client, secondary_auth_client):
    """Detach another user's task returns 404"""
    with allure.step("Create task as second user"):
        user2_task = secondary_auth_client.post('/api/tasks', {
            "title": "User 2 task"
        })
        user2_task_id = user2_task['id']

    with allure.step("Attempt to detach second user's task as first user"):
        response = auth_client.patch(f'/api/tasks/{user2_task_id}/detach',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


# ===== List Project Tasks Tests =====

@allure.feature('Tasks')
@allure.story('Project Association - List Subtasks')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_list_project_tasks_returns_only_subtasks(auth_client):
    """List project tasks returns only tasks associated with that project"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Create subtasks for project"):
        subtask1 = auth_client.post('/api/tasks', {
            "title": "Subtask 1",
            "project_id": project_id
        })
        subtask2 = auth_client.post('/api/tasks', {
            "title": "Subtask 2",
            "project_id": project_id
        })

    with allure.step("Create standalone task"):
        standalone = auth_client.post('/api/tasks', {
            "title": "Standalone task"
        })

    with allure.step("List project tasks"):
        response = auth_client.get(f'/api/projects/{project_id}/tasks')
        project_tasks = response.json

    with allure.step("Verify only subtasks are returned"):
        task_ids = [task['id'] for task in project_tasks]
        assert subtask1['id'] in task_ids
        assert subtask2['id'] in task_ids
        assert standalone['id'] not in task_ids
        assert len(project_tasks) == 2


@allure.feature('Tasks')
@allure.story('Project Association - List Subtasks')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_list_project_tasks_excludes_completed_by_default(auth_client):
    """List project tasks excludes completed tasks by default"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Create incomplete and completed subtasks"):
        incomplete = auth_client.post('/api/tasks', {
            "title": "Incomplete subtask",
            "project_id": project_id
        })
        incomplete_id = incomplete['id']

        completed = auth_client.post('/api/tasks', {
            "title": "Completed subtask",
            "project_id": project_id
        })
        completed_id = completed['id']
        auth_client.patch(f'/api/tasks/{completed_id}/complete')

    with allure.step("List project tasks without include_completed parameter"):
        project_tasks = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify only incomplete subtask is returned"):
        task_ids = [task['id'] for task in project_tasks]
        assert incomplete_id in task_ids
        assert completed_id not in task_ids


@allure.feature('Tasks')
@allure.story('Project Association - List Subtasks')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_list_project_tasks_with_include_completed_true(auth_client):
    """List project tasks includes completed tasks when include_completed=true"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Create incomplete and completed subtasks"):
        incomplete = auth_client.post('/api/tasks', {
            "title": "Incomplete subtask",
            "project_id": project_id
        })
        incomplete_id = incomplete['id']

        completed = auth_client.post('/api/tasks', {
            "title": "Completed subtask",
            "project_id": project_id
        })
        completed_id = completed['id']
        auth_client.patch(f'/api/tasks/{completed_id}/complete')

    with allure.step("List project tasks with include_completed=true"):
        project_tasks = auth_client.get(f'/api/projects/{project_id}/tasks',
                                       params={'include_completed': 'true'})

    with allure.step("Verify both tasks are returned"):
        task_ids = [task['id'] for task in project_tasks]
        assert incomplete_id in task_ids
        assert completed_id in task_ids


@allure.feature('Tasks')
@allure.story('Project Association - List Subtasks')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_list_project_tasks_returns_empty_array_for_project_with_no_tasks(auth_client):
    """List project tasks returns empty array for project with no subtasks"""
    with allure.step("Create project with no subtasks"):
        project = auth_client.post('/api/projects', {
            "title": "Empty Project"
        })
        project_id = project['id']

    with allure.step("List project tasks"):
        response = auth_client.get(f'/api/projects/{project_id}/tasks')
        project_tasks = response.json

    with allure.step("Verify empty array is returned"):
        assert isinstance(project_tasks, list)
        assert len(project_tasks) == 0


@allure.feature('Tasks')
@allure.story('Project Association - List Subtasks')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_list_project_tasks_for_nonexistent_project(auth_client):
    """List project tasks for nonexistent project returns 404"""
    with allure.step("Attempt to list tasks for nonexistent project"):
        response = auth_client.get('/api/projects/999999/tasks',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Project Association - List Subtasks')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_list_project_tasks_for_another_users_project(auth_client, secondary_auth_client):
    """List project tasks for another user's project returns 404"""
    with allure.step("Create project as second user"):
        user2_project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        user2_project_id = user2_project['id']

    with allure.step("Attempt to list second user's project tasks as first user"):
        response = auth_client.get(f'/api/projects/{user2_project_id}/tasks',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


# ===== Create Project Subtask Tests =====

@allure.feature('Tasks')
@allure.story('Project Association - Create Subtask')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_create_subtask_via_project_endpoint(auth_client):
    """Create subtask via project endpoint sets project_id automatically"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Create subtask via project endpoint"):
        subtask = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "New Subtask",
            "description": "Created via project endpoint"
        })

    with allure.step("Verify subtask is automatically associated with project"):
        assert subtask['id']
        assert subtask['title'] == "New Subtask"
        assert subtask['description'] == "Created via project endpoint"
        assert subtask['project_id'] == project_id


@allure.feature('Tasks')
@allure.story('Project Association - Create Subtask')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_create_subtask_with_all_fields(auth_client):
    """Create subtask with all optional fields via project endpoint"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Create subtask with all fields"):
        subtask = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Detailed Subtask",
            "description": "Full description",
            "status": "waiting",
            "active": False
        })

    with allure.step("Verify all fields are set correctly"):
        assert subtask['title'] == "Detailed Subtask"
        assert subtask['description'] == "Full description"
        assert subtask['status'] == "waiting"
        assert subtask['active'] is False
        assert subtask['project_id'] == project_id
        assert subtask['completed'] is False


@allure.feature('Tasks')
@allure.story('Project Association - Create Subtask')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_create_subtask_without_title(auth_client):
    """Create subtask without title returns 400"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Test Project"
        })
        project_id = project['id']

    with allure.step("Attempt to create subtask without title"):
        response = auth_client.post(f'/api/projects/{project_id}/tasks', {},
                                    handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Tasks')
@allure.story('Project Association - Create Subtask')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_create_subtask_for_nonexistent_project(auth_client):
    """Create subtask for nonexistent project returns 404"""
    with allure.step("Attempt to create subtask for nonexistent project"):
        response = auth_client.post('/api/projects/999999/tasks', {
            "title": "Orphaned subtask"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tasks')
@allure.story('Project Association - Create Subtask')
@pytest.mark.tasks
@pytest.mark.projects
@pytest.mark.entity_integration
@allure.severity(allure.severity_level.NORMAL)
def test_create_subtask_for_another_users_project(auth_client, secondary_auth_client):
    """Create subtask for another user's project returns 404"""
    with allure.step("Create project as second user"):
        user2_project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        user2_project_id = user2_project['id']

    with allure.step("Attempt to create subtask for second user's project as first user"):
        response = auth_client.post(f'/api/projects/{user2_project_id}/tasks', {
            "title": "Unauthorized subtask"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404