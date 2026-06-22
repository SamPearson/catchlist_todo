import pytest
import allure


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_task(auth_client):
    """Create task with only required field (title)"""
    with allure.step("Prepare test data"):
        data = {"title": "Test task title"}

    with allure.step("Create new task"):
        response = auth_client.post('/api/tasks', data)

    with allure.step("Verify response structure and values"):
        # Response contains ID and timestamps
        assert response['id']
        assert isinstance(response['id'], int)

        # Title matches input
        assert response['title'] == data['title']
        assert isinstance(response['title'], str)

        # Completion defaults to False
        assert response['completed'] is False
        assert isinstance(response['completed'], bool)

        # Timestamps present
        assert response['created_at']
        assert response['updated_at']
        assert isinstance(response['created_at'], str)
        assert isinstance(response['updated_at'], str)

        # Optional fields present but null
        assert response['description'] is None
        assert response['completed_at'] is None

        # Array fields present and empty
        assert response['tags'] == []
        assert response['principles'] == []
        assert isinstance(response['tags'], list)
        assert isinstance(response['principles'], list)


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_task(auth_client):
    """Retrieve a specific task by ID"""
    with allure.step("Create test task"):
        created = auth_client.post('/api/tasks', {
            "title": "Task for retrieval",
            "description": "Test description"
        })
        task_id = created['id']

    with allure.step("Retrieve the task"):
        retrieved = auth_client.get(f'/api/tasks/{task_id}')

    with allure.step("Verify retrieved task matches created task"):
        assert retrieved['id'] == task_id
        assert retrieved['title'] == created['title']
        assert retrieved['description'] == created['description']
        assert retrieved['completed'] == created['completed']
        assert retrieved['created_at'] == created['created_at']
        assert retrieved['updated_at'] == created['updated_at']


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_tasks(auth_client):
    """Retrieve all tasks for authenticated user"""
    with allure.step("Create multiple test tasks"):
        created_ids = []
        for i in range(3):
            task = auth_client.post('/api/tasks', {
                "title": f"Test task {i+1}"
            })
            created_ids.append(task['id'])

    with allure.step("Retrieve all tasks"):
        response = auth_client.get('/api/tasks')
        tasks = response.json

    with allure.step("Verify response structure"):
        assert isinstance(tasks, list)
        assert len(tasks) >= 3

        # Verify each task has required fields
        for task in tasks:
            assert task['id']
            assert task['title']
            assert 'completed' in task
            assert 'created_at' in task
            assert 'updated_at' in task

    with allure.step("Verify created tasks are in list"):
        retrieved_ids = [task['id'] for task in response]
        for created_id in created_ids:
            assert created_id in retrieved_ids


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_task(auth_client):
    """Update task with multiple fields"""
    with allure.step("Create initial task"):
        created = auth_client.post('/api/tasks', {
            "title": "Original title"
        })
        task_id = created['id']

    with allure.step("Update task"):
        updated = auth_client.patch(f'/api/tasks/{task_id}', {
            "title": "Updated title"
        })

    with allure.step("Verify update"):
        assert updated['id'] == task_id
        assert updated['title'] == "Updated title"
        assert updated['created_at'] == created['created_at']
        assert updated['updated_at'] >= created['updated_at']


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_task(auth_client):
    """Delete task returns 204 No Content"""
    with allure.step("Create task to delete"):
        created = auth_client.post('/api/tasks', {"title": "Delete me"})
        task_id = created['id']

    with allure.step("Delete task"):
        response = auth_client.delete(f'/api/tasks/{task_id}',
                                              handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204

    with allure.step("Verify task is actually deleted"):
        get_response = auth_client.get(f'/api/tasks/{task_id}',
                                               handle_response=False)
        assert get_response.status_code == 404


