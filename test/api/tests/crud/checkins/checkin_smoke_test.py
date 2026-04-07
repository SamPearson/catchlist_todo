import pytest
import allure
from utils.data_factories.entity_factory import create_task, create_checkin


@allure.feature('Checkins')
@allure.story('CRUD Operations')
@pytest.mark.checkins
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_basic_checkin(auth_client):
    """Create a basic checkin with required fields"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for checkin test")
        task_id = task['id']

    with allure.step("Create checkin for task"):
        payload = {
            "target_type": "task",
            "target_id": task_id,
            "note": "Made good progress on this task"
        }
        response = auth_client.post('/api/checkins', data=payload)

    with allure.step("Verify checkin created successfully"):
        assert response['id']
        assert response['target_type'] == "task"
        assert response['target_id'] == task_id
        assert response['note'] == "Made good progress on this task"
        assert response['occurred_at']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Checkins')
@allure.story('CRUD Operations')
@pytest.mark.checkins
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_checkins_for_target(auth_client):
    """List checkins for a specific target entity"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for list checkins test")
        task_id = task['id']

    with allure.step("Create checkin for task"):
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="First checkin"
        )
        checkin_id = checkin['id']

    with allure.step("List checkins for task"):
        response = auth_client.get(
            f'/api/checkins?target_type=task&target_id={task_id}'
        )
        checkins = response.json

    with allure.step("Verify checkin appears in list"):
        assert isinstance(checkins, list)
        assert len(checkins) == 1
        checkin_ids = [c['id'] for c in checkins]
        assert checkin_id in checkin_ids


@allure.feature('Checkins')
@allure.story('CRUD Operations')
@pytest.mark.checkins
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_checkin_by_id(auth_client):
    """Get a specific checkin by ID"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for get checkin test")
        task_id = task['id']

    with allure.step("Create checkin"):
        created = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Checkin to retrieve"
        )
        checkin_id = created['id']

    with allure.step("Get checkin by ID"):
        response = auth_client.get(f'/api/checkins/{checkin_id}')

    with allure.step("Verify checkin details"):
        assert response['id'] == checkin_id
        assert response['target_type'] == "task"
        assert response['target_id'] == task_id
        assert response['note'] == "Checkin to retrieve"
        assert response['occurred_at']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Checkins')
@allure.story('CRUD Operations')
@pytest.mark.checkins
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_checkin_note(auth_client):
    """Update a checkin's note"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for update checkin test")
        task_id = task['id']

    with allure.step("Create checkin"):
        created = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Original note"
        )
        checkin_id = created['id']

    with allure.step("Update checkin note"):
        payload = {"note": "Updated note with new information"}
        response = auth_client.put(f'/api/checkins/{checkin_id}', data=payload)

    with allure.step("Verify note updated"):
        assert response['id'] == checkin_id
        assert response['note'] == "Updated note with new information"
        assert response['target_id'] == task_id


@allure.feature('Checkins')
@allure.story('CRUD Operations')
@pytest.mark.checkins
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_checkin(auth_client):
    """Delete a checkin"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for delete checkin test")
        task_id = task['id']

    with allure.step("Create checkin"):
        created = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Checkin to delete"
        )
        checkin_id = created['id']

    with allure.step("Delete checkin"):
        response = auth_client.delete(
            f'/api/checkins/{checkin_id}',
            handle_response=False
        )

    with allure.step("Verify 204 No Content response"):
        assert response.status_code == 204
        assert response.json is None

    with allure.step("Verify checkin no longer exists"):
        get_response = auth_client.get(
            f'/api/checkins/{checkin_id}',
            handle_response=False
        )
        assert get_response.status_code == 404