import pytest
import allure


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_creates_new_calendar(auth_client, env_manager):
    """Sync calendar creates new calendar with external_uid and external_source='caldav'"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username
        password = env_manager.caldav_password

    with allure.step("Discover available calendars"):
        discover_response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": username,
            "password": password
        })
        calendars = discover_response.json
        assert len(calendars) > 0, "No calendars available for sync"
        remote_uid = calendars[0]['uid']

    with allure.step("Sync remote calendar"):
        sync_response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "password": password,
            "remote_uid": remote_uid
        })

    with allure.step("Verify sync response structure"):
        assert 'calendar_id' in sync_response
        assert 'created_routines' in sync_response
        assert isinstance(sync_response['calendar_id'], int)
        assert isinstance(sync_response['created_routines'], int)

    with allure.step("Verify calendar was created with external fields"):
        calendar_id = sync_response['calendar_id']
        calendar = auth_client.get(f'/api/calendars/{calendar_id}')
        assert calendar['external_uid'] is not None
        assert calendar['external_source'] == 'caldav'


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_returns_created_routines_count(auth_client, env_manager):
    """Sync calendar returns response with calendar_id and created_routines count"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username
        password = env_manager.caldav_password

    with allure.step("Discover available calendars"):
        discover_response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": username,
            "password": password
        })
        calendars = discover_response.json
        assert len(calendars) > 0
        remote_uid = calendars[0]['uid']

    with allure.step("Sync remote calendar"):
        sync_response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "password": password,
            "remote_uid": remote_uid
        })

    with allure.step("Verify response includes calendar_id and created_routines"):
        assert 'calendar_id' in sync_response
        assert 'created_routines' in sync_response
        assert sync_response['calendar_id'] > 0
        assert sync_response['created_routines'] >= 0


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_with_existing_external_uid(auth_client, env_manager):
    """Sync calendar with existing external_uid uses existing calendar (no duplicate)"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username
        password = env_manager.caldav_password

    with allure.step("Discover available calendars"):
        discover_response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": username,
            "password": password
        })
        calendars = discover_response.json
        assert len(calendars) > 0
        remote_uid = calendars[0]['uid']

    with allure.step("Sync calendar first time"):
        first_sync = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "password": password,
            "remote_uid": remote_uid
        })
        first_calendar_id = first_sync['calendar_id']

    with allure.step("Sync same calendar again"):
        second_sync = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "password": password,
            "remote_uid": remote_uid
        })
        second_calendar_id = second_sync['calendar_id']

    with allure.step("Verify same calendar was used (no duplicate)"):
        assert first_calendar_id == second_calendar_id


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_creates_routines_from_recurring_events(auth_client, env_manager):
    """Sync calendar creates routines from recurring events with RRULE"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username
        password = env_manager.caldav_password

    with allure.step("Discover available calendars"):
        discover_response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": username,
            "password": password
        })
        calendars = discover_response.json
        assert len(calendars) > 0
        remote_uid = calendars[0]['uid']

    with allure.step("Sync remote calendar"):
        sync_response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "password": password,
            "remote_uid": remote_uid
        })
        calendar_id = sync_response['calendar_id']
        created_routines = sync_response['created_routines']

    with allure.step("Verify routines were created if recurring events exist"):
        # Get routines for this calendar
        response = auth_client.get('/api/routines')
        all_routines = response.json
        calendar_routines = [r for r in all_routines if r.get('calendar_id') == calendar_id]

        # If routines were created, verify they have RRULE
        if created_routines > 0:
            assert len(calendar_routines) == created_routines
            for routine in calendar_routines:
                assert routine['rrule'] is not None, "Synced routines should have RRULE"


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_without_remote_uid(auth_client, env_manager):
    """Sync calendar without remote_uid returns 400 'remote_uid is required'"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username
        password = env_manager.caldav_password

    with allure.step("Attempt to sync without remote_uid"):
        response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "password": password
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == (
            "remote_uid is required"
        )


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_without_url(auth_client):
    """Sync calendar without url returns 400"""
    with allure.step("Attempt to sync without url"):
        response = auth_client.post('/api/calendars/sync', {
            "username": "test@example.com",
            "password": "password",
            "remote_uid": "some-uid"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == (
            "url is required"
        )


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_without_username(auth_client, env_manager):
    """Sync calendar without username returns 400"""
    with allure.step("Get CalDAV URL"):
        caldav_url = env_manager.caldav_url

    with allure.step("Attempt to sync without username"):
        response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "password": "password",
            "remote_uid": "some-uid"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == (
            "username is required"
        )


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_without_password(auth_client, env_manager):
    """Sync calendar without password returns 400"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username

    with allure.step("Attempt to sync without password"):
        response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "remote_uid": "some-uid"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == (
            "password is required"
        )


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_with_empty_request_body(auth_client):
    """Sync calendar with empty request body returns 400"""
    with allure.step("Attempt to sync with empty body"):
        response = auth_client.post('/api/calendars/sync', {},
                                    handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_with_invalid_credentials(auth_client, env_manager):
    """Sync calendar with invalid credentials returns 401 (CalDAV connection failure)"""
    with allure.step("Get CalDAV URL"):
        caldav_url = env_manager.caldav_url

    with allure.step("Discover available calendars to get valid remote_uid"):
        # First get a valid remote_uid using correct credentials
        username = env_manager.caldav_username
        password = env_manager.caldav_password
        discover_response = auth_client.post('/api/calendars/discover', {
            "url": caldav_url,
            "username": username,
            "password": password
        })
        calendars = discover_response.json
        assert len(calendars) > 0
        remote_uid = calendars[0]['uid']

    with allure.step("Attempt to sync with invalid credentials"):
        response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": "invalid_user",
            "password": "invalid_password",
            "remote_uid": remote_uid
        }, handle_response=False)

    with allure.step("Verify 401 response"):
        assert response.status_code == 401

    with allure.step("Verify error message"):
        assert "authorization failed" in response.json['error'].lower()


@allure.feature('Calendars')
@allure.story('CalDAV Sync')
@pytest.mark.calendars
@pytest.mark.caldav
@allure.severity(allure.severity_level.NORMAL)
def test_sync_calendar_with_nonexistent_remote_uid(auth_client, env_manager):
    """Sync calendar with nonexistent remote_uid returns appropriate error (400 or 401)"""
    with allure.step("Get CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        username = env_manager.caldav_username
        password = env_manager.caldav_password

    with allure.step("Attempt to sync with non-existent remote_uid"):
        remotecal_uid = "nonexistent-uid-12345"
        response = auth_client.post('/api/calendars/sync', {
            "url": caldav_url,
            "username": username,
            "password": password,
            "remote_uid": remotecal_uid
        }, handle_response=False)

    with allure.step("Verify error response (400 or 401)"):
        assert response.status_code in [400, 401]

    with allure.step("Verify error message"):
        assert f"remote calendar {remotecal_uid} not found" in response.json['error'].lower()
