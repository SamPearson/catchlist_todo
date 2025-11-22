import pytest
import allure


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_task(auth_client):
    """Test creating a new task"""
    with allure.step("Prepare test data"):
        data = {
            "content": "Test task content",
            "completed": False
        }

    with allure.step("Create new task"):
        response = auth_client.post('/api/tasks', data)

    with allure.step("Verify response"):
        assert 'id' in response
        assert response['content'] == data['content']
        assert response['completed'] == data['completed']
        assert 'created_at' in response
        assert 'updated_at' in response


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_task(auth_client):
    """Test updating an existing task"""
    with allure.step("Create initial task"):
        initial_data = {
            "content": "Initial task content",
            "completed": False
        }
        create_response = auth_client.post('/api/tasks', initial_data)
        task_id = create_response['id']

    with allure.step("Update the task"):
        update_data = {
            "content": "Updated task content",
            "completed": True
        }
        update_response = auth_client.put(f'/api/tasks/{task_id}', update_data)

    with allure.step("Verify updates"):
        assert update_response['id'] == task_id
        assert update_response['content'] == update_data['content']
        assert update_response['completed'] == update_data['completed']
        assert update_response['updated_at'] > update_response['created_at']


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_task(auth_client):
    """Test deleting a task"""
    with allure.step("Create task to be deleted"):
        data = {
            "content": "Task to be deleted",
            "completed": False
        }
        create_response = auth_client.post('/api/tasks', data)
        task_id = create_response['id']

    with allure.step("Delete the task"):
        delete_response = auth_client.delete(f'/api/tasks/{task_id}', handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify task is deleted"):
        with pytest.raises(Exception) as exc_info:
            auth_client.get(f'/api/tasks/{task_id}')
        assert "404" in str(exc_info.value)


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_task(auth_client):
    """Test retrieving a specific task"""
    with allure.step("Create test task"):
        data = {
            "content": "Task for retrieval test",
            "completed": False
        }
        create_response = auth_client.post('/api/tasks', data)
        task_id = create_response['id']

    with allure.step("Retrieve the task"):
        response = auth_client.get(f'/api/tasks/{task_id}')
        assert response['content'] == data['content']
        assert response['completed'] == data['completed']
        assert response['id'] == task_id


@allure.feature('Tasks')
@allure.story('CRUD Operations')
@pytest.mark.tasks
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_tasks(auth_client):
    """Test retrieving all tasks"""
    with allure.step("Create multiple test tasks"):
        tasks = [
            {
                "content": "First test task",
                "completed": False
            },
            {
                "content": "Second test task",
                "completed": True
            }
        ]
        for task in tasks:
            auth_client.post('/api/tasks', task)

    with allure.step("Retrieve all tasks"):
        response = auth_client.get('/api/tasks')
        assert isinstance(response, list)
        assert len(response) >= 2