import pytest
import allure
from datetime import datetime, timedelta, timezone
from utils.data_factories.entity_factory import create_task, create_checkin


@allure.feature('Checkins')
@allure.story('Get Checkin')
@pytest.mark.checkins
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_checkin_returns_full_object(auth_client):
    """Get checkin returns full object with all fields"""

    with allure.step("Create task and checkin"):
        task = create_task(auth_client, title="Task for get test")
        past_time = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Full checkin object",
            occurred_at=past_time
        )
        checkin_id = checkin['id']

    with allure.step("Get checkin by ID"):
        response = auth_client.get(f'/api/checkins/{checkin_id}')

    with allure.step("Verify all fields present"):
        assert response['id'] == checkin_id
        assert response['user_id']
        assert response['target_type'] == "task"
        assert response['target_id'] == task['id']
        assert response['note'] == "Full checkin object"
        assert response['occurred_at']
        assert response['created_at']
        assert response['updated_at']




@allure.feature('Checkins')
@allure.story('Get Checkin')
@pytest.mark.checkins
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_checkin(auth_client):
    """Get nonexistent checkin returns 404"""

    with allure.step("Attempt to get nonexistent checkin"):
        response = auth_client.get('/api/checkins/999999', handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Checkins')
@allure.story('Get Checkin')
@pytest.mark.checkins
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_checkin(auth_client, secondary_auth_client):
    """Get another user's checkin returns 404"""

    with allure.step("Secondary user creates task and checkin"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_checkin = create_checkin(
            secondary_auth_client,
            target_type="task",
            target_id=secondary_task['id'],
            note="Secondary user's checkin"
        )
        secondary_checkin_id = secondary_checkin['id']

    with allure.step("Primary user attempts to get secondary user's checkin"):
        response = auth_client.get(
            f'/api/checkins/{secondary_checkin_id}',
            handle_response=False
        )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404