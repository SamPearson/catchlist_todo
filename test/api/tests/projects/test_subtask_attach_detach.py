import pytest
import allure


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_subtask_created_in_project_is_attached(auth_client):
    """Subtask created within a project is automatically attached"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask in project"):
        subtask = auth_client.post(f'/api/projects/{project_id}/tasks',
                                   {"title": "Test subtask"})
        subtask_id = subtask['id']

    with allure.step("Verify subtask belongs to project"):
        assert subtask['project_id'] == project_id

    with allure.step("Verify subtask appears in project's task list"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        task_ids = [t['id'] for t in tasks]
        assert subtask_id in task_ids


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_multiple_subtasks_attached_to_project(auth_client):
    """Multiple subtasks can be attached to a single project"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create multiple subtasks in project"):
        subtask_ids = []
        for i in range(3):
            subtask = auth_client.post(f'/api/projects/{project_id}/tasks',
                                       {"title": f"Subtask {i + 1}"})
            subtask_ids.append(subtask['id'])

    with allure.step("Verify all subtasks attached"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        task_ids = [t['id'] for t in tasks]
        for subtask_id in subtask_ids:
            assert subtask_id in task_ids
        assert len(tasks) == 3


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@allure.severity(allure.severity_level.CRITICAL)
def test_same_subtask_cannot_be_in_multiple_projects(auth_client):
    """Subtask belongs to exactly one project"""
    with allure.step("Create two projects"):
        project1 = auth_client.post('/api/projects', {"title": "Project 1"})
        project1_id = project1['id']
        project2 = auth_client.post('/api/projects', {"title": "Project 2"})
        project2_id = project2['id']

    with allure.step("Create subtask in first project"):
        subtask = auth_client.post(f'/api/projects/{project1_id}/tasks',
                                   {"title": "Test subtask"})
        subtask_id = subtask['id']

    with allure.step("Verify subtask only in first project"):
        project1_tasks = auth_client.get(f'/api/projects/{project1_id}/tasks')
        project1_task_ids = [t['id'] for t in project1_tasks]
        assert subtask_id in project1_task_ids

        project2_tasks = auth_client.get(f'/api/projects/{project2_id}/tasks')
        project2_task_ids = [t['id'] for t in project2_tasks]
        assert subtask_id not in project2_task_ids


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_subtask_removes_from_project(auth_client):
    """Deleting a subtask removes it from project's task list"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask in project"):
        subtask = auth_client.post(f'/api/projects/{project_id}/tasks',
                                   {"title": "Test subtask"})
        subtask_id = subtask['id']

    with allure.step("Verify subtask in project"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        task_ids = [t['id'] for t in tasks]
        assert subtask_id in task_ids

    with allure.step("Delete subtask"):
        auth_client.delete(f'/api/projects/{project_id}/tasks/{subtask_id}',
                           handle_response=False)

    with allure.step("Verify subtask removed from project"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks?include_completed=true')
        task_ids = [t['id'] for t in tasks]
        assert subtask_id not in task_ids


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@allure.severity(allure.severity_level.CRITICAL)
def test_completed_subtask_hidden_from_default_list(auth_client):
    """Completed subtasks are hidden from project list by default"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create active and completed subtasks"):
        active = auth_client.post(f'/api/projects/{project_id}/tasks',
                                  {"title": "Active"})
        active_id = active['id']

        completed = auth_client.post(f'/api/projects/{project_id}/tasks',
                                     {"title": "Completed"})
        completed_id = completed['id']
        auth_client.put(f'/api/projects/{project_id}/tasks/{completed_id}',
                        {"completed": True})

    with allure.step("Verify active shown, completed hidden by default"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        task_ids = [t['id'] for t in tasks]
        assert active_id in task_ids
        assert completed_id not in task_ids

    with allure.step("Verify completed shown with include_completed=true"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks?include_completed=true')
        task_ids = [t['id'] for t in tasks]
        assert active_id in task_ids
        assert completed_id in task_ids


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@allure.severity(allure.severity_level.CRITICAL)
def test_update_subtask_maintains_project_attachment(auth_client):
    """Updating a subtask maintains its attachment to project"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask"):
        subtask = auth_client.post(f'/api/projects/{project_id}/tasks',
                                   {"title": "Original title"})
        subtask_id = subtask['id']
        original_project_id = subtask['project_id']

    with allure.step("Update subtask"):
        updated = auth_client.put(f'/api/projects/{project_id}/tasks/{subtask_id}',
                                  {"title": "Updated title"})

    with allure.step("Verify attachment maintained"):
        assert updated['project_id'] == original_project_id
        assert updated['project_id'] == project_id

        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        task_ids = [t['id'] for t in tasks]
        assert subtask_id in task_ids


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@allure.severity(allure.severity_level.CRITICAL)
def test_deleting_project_removes_all_subtasks(auth_client):
    """Deleting a project cascades to remove all its subtasks"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create multiple subtasks"):
        subtask_ids = []
        for i in range(3):
            subtask = auth_client.post(f'/api/projects/{project_id}/tasks',
                                       {"title": f"Subtask {i + 1}"})
            subtask_ids.append(subtask['id'])

    with allure.step("Verify subtasks exist"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        assert len(tasks) == 3

    with allure.step("Delete project"):
        auth_client.delete(f'/api/projects/{project_id}',
                           handle_response=False)

    with allure.step("Verify project deleted"):
        response = auth_client.get(f'/api/projects/{project_id}',
                                   handle_response=False)
        assert response.status_code == 404

    with allure.step("Verify all subtasks cascade deleted"):
        # Attempt to list tasks from deleted project
        response = auth_client.get(f'/api/projects/{project_id}/tasks',
                                   handle_response=False)
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_subtask_list_ordered_by_creation(auth_client):
    """Subtasks in project list maintain creation order"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtasks in sequence"):
        subtask_ids = []
        for i in range(3):
            subtask = auth_client.post(f'/api/projects/{project_id}/tasks',
                                       {"title": f"Subtask {i + 1}"})
            subtask_ids.append(subtask['id'])

    with allure.step("Retrieve subtasks and verify order"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        retrieved_ids = [t['id'] for t in tasks]

        # Verify same order as creation
        for i, subtask_id in enumerate(subtask_ids):
            assert retrieved_ids[i] == subtask_id


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@allure.severity(allure.severity_level.CRITICAL)
def test_empty_project_has_no_subtasks(auth_client):
    """New project with no subtasks returns empty list"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Empty project"})
        project_id = project['id']

    with allure.step("Retrieve subtasks from empty project"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify empty list"):
        assert isinstance(tasks, list)
        assert len(tasks) == 0


@allure.feature('Projects')
@allure.story('Subtask Management')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.attach_detach
@allure.severity(allure.severity_level.CRITICAL)
def test_subtask_fields_correct_after_project_attachment(auth_client):
    """Subtask has correct project association after creation"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask with details"):
        subtask = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Test subtask",
            "description": "Test description"
        })
        subtask_id = subtask['id']

    with allure.step("Verify subtask fields and project attachment"):
        # Verify via project tasks list
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')
        found_subtask = next(t for t in tasks if t['id'] == subtask_id)

        assert found_subtask['title'] == "Test subtask"
        assert found_subtask['description'] == "Test description"
        assert found_subtask['project_id'] == project_id
        assert found_subtask['completed'] is False
        assert found_subtask['created_at']
        assert found_subtask['updated_at']