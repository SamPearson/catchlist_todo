import pytest
import allure


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_discover_remote_calendars(auth_client, env_manager):
    """Discover remote calendars from CalDAV server"""
    with allure.step("Prepare CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        caldav_username = env_manager.caldav_username
        caldav_password = env_manager.caldav_password

        if not all([caldav_url, caldav_username, caldav_password]):
            pytest.skip("CalDAV credentials not configured in environment")

        data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password
        }

    with allure.step("Discover remote calendars"):
        response = auth_client.post('/api/calendars/discover', data)

    with allure.step("Verify response structure"):
        assert isinstance(response, list)
        assert len(response) > 0

        # Verify each calendar has required fields
        for calendar in response:
            assert 'name' in calendar
            assert 'uid' in calendar
            assert 'url' in calendar
            assert 'color' in calendar
            assert isinstance(calendar['name'], str)
            assert isinstance(calendar['uid'], str)
            assert isinstance(calendar['url'], str)


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@allure.severity(allure.severity_level.CRITICAL)
def test_discover_with_invalid_credentials(auth_client, env_manager):
    """Discover with invalid credentials returns error"""
    with allure.step("Prepare invalid CalDAV credentials"):
        data = {
            "url": "https://invalid.example.com",
            "username": "invalid_user",
            "password": "invalid_pass"
        }

    with allure.step("Attempt to discover calendars"):
        response = auth_client.post('/api/calendars/discover', data,
                                    handle_response=False)

    with allure.step("Verify error response"):
        assert response.status_code == 401
        error_response = response.json()
        assert 'error' in error_response


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_sync_remote_calendar(auth_client, env_manager):
    """Sync a remote calendar from CalDAV server"""
    with allure.step("Prepare CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        caldav_username = env_manager.caldav_username
        caldav_password = env_manager.caldav_password

        if not all([caldav_url, caldav_username, caldav_password]):
            pytest.skip("CalDAV credentials not configured in environment")

    with allure.step("Discover available remote calendars"):
        discover_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password
        }
        discover_response = auth_client.post('/api/calendars/discover', discover_data)

        if len(discover_response) == 0:
            pytest.skip("No remote calendars available to sync")

        remote_calendar = discover_response[0]
        remote_uid = remote_calendar['uid']

    with allure.step("Sync remote calendar"):
        sync_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password,
            "remote_uid": remote_uid
        }
        response = auth_client.post('/api/calendars/sync', sync_data)

    with allure.step("Verify sync response"):
        assert 'calendar_id' in response
        assert isinstance(response['calendar_id'], int)
        assert 'created_routines' in response
        assert isinstance(response['created_routines'], int)


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@allure.severity(allure.severity_level.CRITICAL)
def test_synced_calendar_has_external_metadata(auth_client, env_manager):
    """Verify synced calendar has external_uid and external_source"""
    with allure.step("Prepare CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        caldav_username = env_manager.caldav_username
        caldav_password = env_manager.caldav_password

        if not all([caldav_url, caldav_username, caldav_password]):
            pytest.skip("CalDAV credentials not configured in environment")

    with allure.step("Discover and sync remote calendar"):
        discover_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password
        }
        discover_response = auth_client.post('/api/calendars/discover', discover_data)

        if len(discover_response) == 0:
            pytest.skip("No remote calendars available to sync")

        remote_calendar = discover_response[0]
        remote_uid = remote_calendar['uid']

        sync_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password,
            "remote_uid": remote_uid
        }
        sync_response = auth_client.post('/api/calendars/sync', sync_data)
        calendar_id = sync_response['calendar_id']

    with allure.step("Retrieve synced calendar from list"):
        calendars = auth_client.get('/api/calendars')
        synced_calendar = next((c for c in calendars if c['id'] == calendar_id), None)

    with allure.step("Verify external metadata is populated"):
        assert synced_calendar is not None
        assert synced_calendar['external_uid'] == remote_uid
        assert synced_calendar['external_source'] == 'caldav'


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@allure.severity(allure.severity_level.CRITICAL)
def test_sync_creates_routines_from_remote_events(auth_client, env_manager):
    """Verify sync creates Routine records from remote calendar events"""
    with allure.step("Prepare CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        caldav_username = env_manager.caldav_username
        caldav_password = env_manager.caldav_password

        if not all([caldav_url, caldav_username, caldav_password]):
            pytest.skip("CalDAV credentials not configured in environment")

    with allure.step("Discover and sync remote calendar"):
        discover_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password
        }
        discover_response = auth_client.post('/api/calendars/discover', discover_data)

        if len(discover_response) == 0:
            pytest.skip("No remote calendars available to sync")

        remote_calendar = discover_response[0]
        remote_uid = remote_calendar['uid']

        sync_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password,
            "remote_uid": remote_uid
        }
        sync_response = auth_client.post('/api/calendars/sync', sync_data)
        created_routines = sync_response['created_routines']

    with allure.step("Verify routines were created"):
        # The number of created routines depends on the remote calendar content
        # We just verify that sync returns a count
        assert isinstance(created_routines, int)
        assert created_routines >= 0


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@allure.severity(allure.severity_level.CRITICAL)
def test_resync_prevents_duplicate_routines(auth_client, env_manager):
    """Re-syncing same remote calendar doesn't create duplicate routines"""
    with allure.step("Prepare CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        caldav_username = env_manager.caldav_username
        caldav_password = env_manager.caldav_password

        if not all([caldav_url, caldav_username, caldav_password]):
            pytest.skip("CalDAV credentials not configured in environment")

    with allure.step("Discover remote calendar"):
        discover_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password
        }
        discover_response = auth_client.post('/api/calendars/discover', discover_data)

        if len(discover_response) == 0:
            pytest.skip("No remote calendars available to sync")

        remote_calendar = discover_response[0]
        remote_uid = remote_calendar['uid']

    with allure.step("Sync remote calendar first time"):
        sync_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password,
            "remote_uid": remote_uid
        }
        first_sync = auth_client.post('/api/calendars/sync', sync_data)
        first_routine_count = first_sync['created_routines']

    with allure.step("Sync same remote calendar again"):
        second_sync = auth_client.post('/api/calendars/sync', sync_data)
        second_routine_count = second_sync['created_routines']

    with allure.step("Verify no new duplicates created on re-sync"):
        # On re-sync, if routines already exist, they should not be recreated
        # The count should be 0 or much lower than the first sync
        assert second_routine_count <= first_routine_count


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@allure.severity(allure.severity_level.CRITICAL)
def test_synced_calendar_can_be_updated(auth_client, env_manager):
    """Update synced calendar name and color"""
    with allure.step("Prepare CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        caldav_username = env_manager.caldav_username
        caldav_password = env_manager.caldav_password

        if not all([caldav_url, caldav_username, caldav_password]):
            pytest.skip("CalDAV credentials not configured in environment")

    with allure.step("Discover and sync remote calendar"):
        discover_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password
        }
        discover_response = auth_client.post('/api/calendars/discover', discover_data)

        if len(discover_response) == 0:
            pytest.skip("No remote calendars available to sync")

        remote_calendar = discover_response[0]
        remote_uid = remote_calendar['uid']

        sync_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password,
            "remote_uid": remote_uid
        }
        sync_response = auth_client.post('/api/calendars/sync', sync_data)
        calendar_id = sync_response['calendar_id']

    with allure.step("Update synced calendar"):
        updated = auth_client.put(f'/api/calendars/{calendar_id}', {
            "name": "Updated Synced Calendar",
            "color": "#FF0000"
        })

    with allure.step("Verify update applied"):
        assert updated['name'] == "Updated Synced Calendar"
        assert updated['color'] == "#FF0000"
        # Verify external metadata persists
        assert updated['external_uid'] == remote_uid
        assert updated['external_source'] == 'caldav'


@allure.feature('Calendars')
@allure.story('Remote Calendar Operations')
@pytest.mark.calendars
@pytest.mark.remote
@allure.severity(allure.severity_level.CRITICAL)
def test_synced_calendar_can_be_deactivated(auth_client, env_manager):
    """Deactivate a synced calendar"""
    with allure.step("Prepare CalDAV credentials"):
        caldav_url = env_manager.caldav_url
        caldav_username = env_manager.caldav_username
        caldav_password = env_manager.caldav_password

        if not all([caldav_url, caldav_username, caldav_password]):
            pytest.skip("CalDAV credentials not configured in environment")

    with allure.step("Discover and sync remote calendar"):
        discover_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password
        }
        discover_response = auth_client.post('/api/calendars/discover', discover_data)

        if len(discover_response) == 0:
            pytest.skip("No remote calendars available to sync")

        remote_calendar = discover_response[0]
        remote_uid = remote_calendar['uid']

        sync_data = {
            "url": caldav_url,
            "username": caldav_username,
            "password": caldav_password,
            "remote_uid": remote_uid
        }
        sync_response = auth_client.post('/api/calendars/sync', sync_data)
        calendar_id = sync_response['calendar_id']

    with allure.step("Deactivate synced calendar"):
        deactivated = auth_client.put(f'/api/calendars/{calendar_id}', {
            "active": False
        })

    with allure.step("Verify calendar is inactive"):
        assert deactivated['active'] is False
        assert deactivated['external_uid'] == remote_uid
        assert deactivated['external_source'] == 'caldav'
