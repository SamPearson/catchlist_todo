import pytest
import allure


@allure.feature('Calendars')
@allure.story('Get Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_calendar_returns_full_object(auth_client):
    """Get calendar returns full object with all fields including tags and principles"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar",
            "color": "#ff5733"
        })
        calendar_id = created['id']

    with allure.step("Retrieve calendar by ID"):
        calendar = auth_client.get(f'/api/calendars/{calendar_id}')

    with allure.step("Verify all fields are present"):
        assert calendar['id'] == calendar_id
        assert calendar['user_id']
        assert isinstance(calendar['user_id'], int)
        assert calendar['name'] == "Test Calendar"
        assert calendar['color'] == "#ff5733"
        assert calendar['active'] is True
        assert calendar['external_uid'] is None
        assert calendar['external_source'] is None
        assert 'tags' in calendar
        assert isinstance(calendar['tags'], list)
        assert 'principles' in calendar
        assert isinstance(calendar['principles'], list)
        assert calendar['created_at']
        assert calendar['updated_at']


@allure.feature('Calendars')
@allure.story('Get Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_calendar(auth_client):
    """Get nonexistent calendar returns 404"""
    with allure.step("Attempt to retrieve non-existent calendar"):
        response = auth_client.get('/api/calendars/999999',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Calendars')
@allure.story('Get Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_calendar(auth_client, secondary_auth_client):
    """Get another user's calendar returns 404 (acts as if doesn't exist)"""
    with allure.step("Primary user creates calendar"):
        primary_cal = auth_client.post('/api/calendars', {
            "name": "Primary User Calendar"
        })
        primary_cal_id = primary_cal['id']

    with allure.step("Secondary user attempts to access primary user's calendar"):
        response = secondary_auth_client.get(f'/api/calendars/{primary_cal_id}',
                                             handle_response=False)

    with allure.step("Verify 404 response (not 403)"):
        assert response.status_code == 404