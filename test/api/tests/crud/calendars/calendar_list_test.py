import pytest
import allure


@allure.feature('Calendars')
@allure.story('List Calendars')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_calendars_excludes_inactive_by_default(auth_client):
    """List calendars excludes inactive calendars by default"""
    with allure.step("Create active and inactive calendars"):
        active = auth_client.post('/api/calendars', {"name": "Active Calendar"})
        active_id = active['id']

        inactive_cal = auth_client.post('/api/calendars', {"name": "Inactive Calendar"})
        inactive_id = inactive_cal['id']
        auth_client.patch(f'/api/calendars/{inactive_id}/deactivate')

    with allure.step("List calendars without include_inactive parameter"):
        response = auth_client.get('/api/calendars')
        calendars = response.json

    with allure.step("Verify only active calendar is returned"):
        calendar_ids = [cal['id'] for cal in calendars]
        assert active_id in calendar_ids
        assert inactive_id not in calendar_ids


@allure.feature('Calendars')
@allure.story('List Calendars')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_calendars_with_include_inactive_true(auth_client):
    """List calendars includes inactive calendars when include_inactive=true"""
    with allure.step("Create active and inactive calendars"):
        active = auth_client.post('/api/calendars', {"name": "Active Calendar"})
        active_id = active['id']

        inactive_cal = auth_client.post('/api/calendars', {"name": "Inactive Calendar"})
        inactive_id = inactive_cal['id']
        auth_client.patch(f'/api/calendars/{inactive_id}/deactivate')

    with allure.step("List calendars with include_inactive=true"):
        response = auth_client.get('/api/calendars', params={'include_inactive': 'true'})
        calendars = response.json

    with allure.step("Verify both calendars are returned"):
        calendar_ids = [cal['id'] for cal in calendars]
        assert active_id in calendar_ids
        assert inactive_id in calendar_ids


@allure.feature('Calendars')
@allure.story('List Calendars')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_calendars_with_include_inactive_false(auth_client):
    """List calendars excludes inactive calendars when include_inactive=false (explicit)"""
    with allure.step("Create active and inactive calendars"):
        active = auth_client.post('/api/calendars', {"name": "Active Calendar"})
        active_id = active['id']

        inactive_cal = auth_client.post('/api/calendars', {"name": "Inactive Calendar"})
        inactive_id = inactive_cal['id']
        auth_client.patch(f'/api/calendars/{inactive_id}/deactivate')

    with allure.step("List calendars with include_inactive=false"):
        response = auth_client.get('/api/calendars', params={'include_inactive': 'false'})
        calendars = response.json

    with allure.step("Verify only active calendar is returned"):
        calendar_ids = [cal['id'] for cal in calendars]
        assert active_id in calendar_ids
        assert inactive_id not in calendar_ids


@allure.feature('Calendars')
@allure.story('List Calendars')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_calendars_returns_empty_array(auth_client):
    """List calendars returns empty array for user with no calendars"""
    with allure.step("List calendars for fresh user"):
        response = auth_client.get('/api/calendars')
        calendars = response.json

    with allure.step("Verify empty array is returned"):
        assert isinstance(calendars, list)
        assert len(calendars) == 0


@allure.feature('Calendars')
@allure.story('List Calendars')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_calendars_user_isolation(auth_client, secondary_auth_client):
    """List calendars only returns the authenticated user's calendars"""
    with allure.step("Create calendar for first user"):
        user1_cal = auth_client.post('/api/calendars', {"name": "User 1 Calendar"})
        user1_cal_id = user1_cal['id']

    with allure.step("Create calendar for second user"):
        user2_cal = secondary_auth_client.post('/api/calendars', {"name": "User 2 Calendar"})
        user2_cal_id = user2_cal['id']

    with allure.step("List calendars for second user"):
        response = secondary_auth_client.get('/api/calendars')
        user2_calendars = response.json

    with allure.step("Verify user 2 only sees their own calendar"):
        calendar_ids = [cal['id'] for cal in user2_calendars]
        assert user2_cal_id in calendar_ids
        assert user1_cal_id not in calendar_ids