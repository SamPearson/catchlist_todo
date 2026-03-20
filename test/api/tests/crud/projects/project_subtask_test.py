
import pytest
import allure


@allure.feature('Projects')
@allure.story('List Project Tasks')
@pytest.mark.projects
@pytest.mark.subtasks
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_for_project_with_no_subtasks(auth_client):
    """List tasks for project with no subtasks returns empty array"""
    with allure.step("Create project without subtasks"):
        project = auth_client.post('/api/projects', {
            "title": "Project with no subtasks"
        })
        project_id = project['id']

    with allure.step("List tasks for project"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify empty array returned"):
        assert isinstance(tasks, list)
        assert len(tasks) == 0


@allure.feature('Projects')
@allure.story('List Project Tasks')
@pytest.mark.projects
@pytest.mark.subtasks
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_for_project_with_subtasks(auth_client):
    """List tasks for project with subtasks returns all subtasks"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project with subtasks"
        })
        project_id = project['id']

    with allure.step("Create 2 subtasks"):
        task1 = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Subtask 1"
        })
        task2 = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Subtask 2"
        })
        task1_id = task1['id']
        task2_id = task2['id']

    with allure.step("List tasks for project"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify both subtasks returned"):
        assert isinstance(tasks, list)
        assert len(tasks) == 2
        task_ids = [task['id'] for task in tasks]
        assert task1_id in task_ids
        assert task2_id in task_ids


@allure.feature('Projects')
@allure.story('List Project Tasks')
@pytest.mark.projects
@pytest.mark.subtasks
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_excludes_completed_by_default(auth_client):
    """List tasks excludes completed subtasks by default"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project with mixed subtasks"
        })
        project_id = project['id']

    with allure.step("Create 2 subtasks, complete 1"):
        incomplete = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Incomplete subtask"
        })
        incomplete_id = incomplete['id']

        completed = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Completed subtask"
        })
        completed_id = completed['id']
        auth_client.patch(f'/api/tasks/{completed_id}/complete')

    with allure.step("List tasks without include_completed parameter"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify only incomplete subtask returned"):
        task_ids = [task['id'] for task in tasks]
        assert incomplete_id in task_ids
        assert completed_id not in task_ids


@allure.feature('Projects')
@allure.story('List Project Tasks')
@pytest.mark.projects
@pytest.mark.subtasks
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_with_include_completed_true(auth_client):
    """List tasks includes completed subtasks when include_completed=true"""
    with allure.step("Create project"):
        project = auth_client.post('/api/projects', {
            "title": "Project with mixed subtasks"
        })
        project_id = project['id']

    with allure.step("Create 2 subtasks, complete 1"):
        incomplete = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Incomplete subtask"
        })
        incomplete_id = incomplete['id']

        completed = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Completed subtask"
        })
        completed_id = completed['id']
        auth_client.patch(f'/api/tasks/{completed_id}/complete')

    with allure.step("List tasks with include_completed=true"):
        tasks = auth_client.get(f'/api/projects/{project_id}/tasks',
                               params={'include_completed': 'true'})

    with allure.step("Verify both subtasks returned"):
        task_ids = [task['id'] for task in tasks]
        assert incomplete_id in task_ids
        assert completed_id in task_ids


@allure.feature('Projects')
@allure.story('List Project Tasks')
@pytest.mark.projects
@pytest.mark.subtasks
@allure.severity(allure.severity_level.NORMAL)
def test_list_tasks_for_nonexistent_project(auth_client):
    """List tasks for nonexistent project returns 404"""
    with allure.step("Attempt to list tasks for nonexistent project"):
        response = auth_client.get('/api/projects/999999/tasks',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404