import pytest
import allure
from utils.data_factories.entity_factory import create_task, create_checkin


@allure.feature('Checkins')
@allure.story('Delete Checkin')
@pytest.mark.checkins
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_checkin_returns_204(auth_client):
    """Delete checkin returns 204 No Content"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for delete test")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Checkin to be deleted"
        )
        checkin_id = checkin['id']

    with allure.step("Delete checkin"):
        response = auth_client.delete(
            f'/api/checkins/{checkin_id}',
            handle_response=False
        )

    with allure.step("Verify 204 No Content response"):
        assert response.status_code == 204
        assert response.json is None


@allure.feature('Checkins')
@allure.story('Delete Checkin')
@pytest.mark.checkins
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_checkin_actually_removes_it(auth_client):
    """Delete checkin actually removes it from database"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for deletion verification")
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Checkin to verify deletion"
        )
        checkin_id = checkin['id']

    with allure.step("Verify checkin exists before deletion"):
        get_before = auth_client.get(f'/api/checkins/{checkin_id}')
        assert get_before['id'] == checkin_id

    with allure.step("Delete checkin"):
        delete_response = auth_client.delete(
            f'/api/checkins/{checkin_id}',
            handle_response=False
        )
        assert delete_response.status_code == 204

    with allure.step("Verify checkin no longer exists"):
        get_after = auth_client.get(
            f'/api/checkins/{checkin_id}',
            handle_response=False
        )
        assert get_after.status_code == 404


@allure.feature('Checkins')
@allure.story('Delete Checkin')
@pytest.mark.checkins
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_checkin(auth_client):
    """Delete nonexistent checkin returns 404"""

    with allure.step("Attempt to delete nonexistent checkin"):
        response = auth_client.delete(
            '/api/checkins/999999',
            handle_response=False
        )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Checkins')
@allure.story('Delete Checkin')
@pytest.mark.checkins
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_users_checkin(auth_client, secondary_auth_client):
    """Delete another user's checkin returns 404"""

    with allure.step("Secondary user creates task and checkin"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_checkin = create_checkin(
            secondary_auth_client,
            target_type="task",
            target_id=secondary_task['id'],
            note="Secondary user's checkin"
        )
        secondary_checkin_id = secondary_checkin['id']

    with allure.step("Primary user attempts to delete secondary user's checkin"):
        response = auth_client.delete(
            f'/api/checkins/{secondary_checkin_id}',
            handle_response=False
        )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404

    with allure.step("Verify secondary user's checkin still exists"):
        verify_exists = secondary_auth_client.get(
            f'/api/checkins/{secondary_checkin_id}'
        )
        assert verify_exists['id'] == secondary_checkin_id