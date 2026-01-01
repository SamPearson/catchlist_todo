import pytest
import allure


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_task_with_required_fields(auth_client):
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
def test_create_task_with_description(auth_client):
    """Create task with title and description"""
    with allure.step("Prepare test data"):
        data = {
            "title": "Task with description",
            "description": "This is a detailed description of the task"
        }

    with allure.step("Create new task"):
        response = auth_client.post('/api/tasks', data)

    with allure.step("Verify description is stored"):
        assert response['description'] == data['description']
        assert isinstance(response['description'], str)


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_task_with_completed_status(auth_client):
    """Create task with completed status"""
    with allure.step("Prepare test data"):
        data = {
            "title": "Completed task",
            "completed": True
        }

    with allure.step("Create new task"):
        response = auth_client.post('/api/tasks', data)

    with allure.step("Verify completed status"):
        assert response['completed'] is True


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_multiple_tasks(auth_client):
    """Create multiple tasks to verify independence"""
    with allure.step("Create first task"):
        task1 = auth_client.post('/api/tasks', {"title": "Task 1"})
        task1_id = task1['id']

    with allure.step("Create second task"):
        task2 = auth_client.post('/api/tasks', {"title": "Task 2"})
        task2_id = task2['id']

    with allure.step("Verify tasks are independent"):
        assert task1_id != task2_id
        assert task1['title'] != task2['title']
        # Timestamps should be close but not identical
        assert task1['created_at'] <= task2['created_at']


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_task_by_id(auth_client):
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
def test_get_all_tasks_returns_list(auth_client):
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

    with allure.step("Verify response structure"):
        assert isinstance(response, list)
        assert len(response) >= 3

        # Verify each task has required fields
        for task in response:
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
def test_update_task_title(auth_client):
    """Update task title"""
    with allure.step("Create initial task"):
        created = auth_client.post('/api/tasks', {
            "title": "Original title"
        })
        task_id = created['id']

    with allure.step("Update task title"):
        updated = auth_client.put(f'/api/tasks/{task_id}', {
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
def test_update_task_completion_status(auth_client):
    """Update task completion status"""
    with allure.step("Create incomplete task"):
        created = auth_client.post('/api/tasks', {
            "title": "Test task",
            "completed": False
        })
        task_id = created['id']

    with allure.step("Mark task as complete"):
        updated = auth_client.put(f'/api/tasks/{task_id}', {
            "completed": True
        })

    with allure.step("Verify completion status changed"):
        assert updated['completed'] is True
        assert updated['title'] == created['title']  # Title unchanged


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_task_description(auth_client):
    """Update task description"""
    with allure.step("Create task with description"):
        created = auth_client.post('/api/tasks', {
            "title": "Test task",
            "description": "Original description"
        })
        task_id = created['id']

    with allure.step("Update description"):
        updated = auth_client.put(f'/api/tasks/{task_id}', {
            "description": "New description"
        })

    with allure.step("Verify description updated"):
        assert updated['description'] == "New description"
        assert updated['title'] == created['title']  # Title unchanged


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_multiple_fields(auth_client):
    """Update multiple task fields at once"""
    with allure.step("Create initial task"):
        created = auth_client.post('/api/tasks', {
            "title": "Original",
            "description": "Original description",
            "completed": False
        })
        task_id = created['id']

    with allure.step("Update multiple fields"):
        updated = auth_client.put(f'/api/tasks/{task_id}', {
            "title": "New title",
            "description": "New description",
            "completed": True
        })

    with allure.step("Verify all updates applied"):
        assert updated['title'] == "New title"
        assert updated['description'] == "New description"
        assert updated['completed'] is True


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_preserves_timestamps(auth_client):
    """Verify created_at doesn't change on update"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {"title": "Test"})
        original_created_at = created['created_at']

    with allure.step("Update task"):
        updated = auth_client.put(f'/api/tasks/{created["id"]}', {
            "title": "Updated"
        })

    with allure.step("Verify timestamps"):
        assert updated['created_at'] == original_created_at
        assert updated['updated_at'] >= original_created_at


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_task_returns_204(auth_client):
    """Delete task returns 204 No Content"""
    with allure.step("Create task to delete"):
        created = auth_client.post('/api/tasks', {"title": "Delete me"})
        task_id = created['id']

    with allure.step("Delete task"):
        response = auth_client.delete(f'/api/tasks/{task_id}',
                                     handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_task_removes_from_list(auth_client):
    """Verify deleted task no longer appears in list"""
    with allure.step("Create task"):
        created = auth_client.post('/api/tasks', {"title": "To delete"})
        task_id = created['id']

    with allure.step("Verify task in list"):
        tasks_before = auth_client.get('/api/tasks')
        task_ids_before = [t['id'] for t in tasks_before]
        assert task_id in task_ids_before

    with allure.step("Delete task"):
        auth_client.delete(f'/api/tasks/{task_id}', handle_response=False)

    with allure.step("Verify task removed from list"):
        tasks_after = auth_client.get('/api/tasks')
        task_ids_after = [t['id'] for t in tasks_after]
        assert task_id not in task_ids_after


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_task_cannot_be_retrieved(auth_client):
    """Verify deleted task returns 404 on GET"""
    with allure.step("Create and delete task"):
        created = auth_client.post('/api/tasks', {"title": "Delete me"})
        task_id = created['id']
        auth_client.delete(f'/api/tasks/{task_id}', handle_response=False)

    with allure.step("Attempt to retrieve deleted task"):
        response = auth_client.get(f'/api/tasks/{task_id}',
                                  handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404