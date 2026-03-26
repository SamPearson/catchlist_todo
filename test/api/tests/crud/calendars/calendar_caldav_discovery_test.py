import pytest
import allure


@allure.feature('Calendars')
@allure.story('CalDAV Discovery')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_discover_calendars_with_valid_credentials(auth_client, env_manager):
    """Discover calendars with valid credentials returns list of remote calendars"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username
        password = env_manager.caldav_password

    with allure.step("Discover remote calendars"):
        response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": username,
            "password": password
        })
        calendars = response.json

    with allure.step("Verify list of calendars returned"):
        assert isinstance(calendars, list)
        assert len(calendars) > 0, "Expected at least one calendar from test CalDAV server"

    with allure.step("Verify calendar objects have required fields"):
        for calendar in calendars:
            assert 'name' in calendar
            assert 'uid' in calendar
            assert 'url' in calendar
            assert 'color' in calendar
            assert isinstance(calendar['name'], str)
            assert isinstance(calendar['uid'], str)
            assert isinstance(calendar['url'], str)


@allure.feature('Calendars')
@allure.story('CalDAV Discovery')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_discover_calendars_without_url(auth_client):
    """Discover calendars without url returns 400 (missing required field)"""
    with allure.step("Attempt to discover without url"):
        response = auth_client.post('/api/calendars/discover', {
            "username": "test@example.com",
            "password": "password"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "url is required" in response.json['error']


@allure.feature('Calendars')
@allure.story('CalDAV Discovery')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_discover_calendars_without_username(auth_client, env_manager):
    """Discover calendars without username returns 400 (missing required field)"""
    with allure.step("Get CalDAV URL"):
        caldav_url = env_manager.caldav_url

    with allure.step("Attempt to discover without username"):
        response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "password": "password"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "username is required" in response.json['error']


@allure.feature('Calendars')
@allure.story('CalDAV Discovery')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_discover_calendars_without_password(auth_client, env_manager):
    """Discover calendars without password returns 400 (missing required field)"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username

    with allure.step("Attempt to discover without password"):
        response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": username
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "password is required" in response.json['error']


@allure.feature('Calendars')
@allure.story('CalDAV Discovery')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_discover_calendars_with_empty_request_body(auth_client):
    """Discover calendars with empty request body returns 400"""
    with allure.step("Attempt to discover with empty body"):
        response = auth_client.post('/api/calendars/discover', {},
                                    handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Calendars')
@allure.story('CalDAV Discovery')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_discover_calendars_with_invalid_credentials(auth_client, env_manager):
    """Discover calendars with invalid credentials returns 401 (CalDAV connection failure)"""
    with allure.step("Get CalDAV URL"):
        caldav_url = env_manager.caldav_url

    with allure.step("Attempt to discover with invalid credentials"):
        response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": "invalid_user@example.com",
            "password": "wrong_password"
        }, handle_response=False)

    with allure.step("Verify 401 response"):
        assert response.status_code == 401

    with allure.step("Verify error message"):
        assert "authorization failed" in response.json['error'].lower()


@allure.feature('Calendars')
@allure.story('CalDAV Discovery')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_discover_calendars_with_malformed_url(auth_client):
    """Discover calendars with malformed url returns 401 (CalDAV connection failure)"""
    with allure.step("Attempt to discover with malformed URL"):
        response = auth_client.post('/api/calendars/discover', {
            "url": "not-a-valid-url",
            "username": "test@example.com",
            "password": "password"
        }, handle_response=False)

    with allure.step("Verify 401 response"):
        assert response.status_code == 401

    with allure.step("Verify error message"):
        assert "invalid url" in response.json['error'].lower()