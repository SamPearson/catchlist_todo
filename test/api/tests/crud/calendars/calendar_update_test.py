import pytest
import allure


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_name(auth_client):
    """Update calendar name and verify change persists"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Original Name"
        })
        calendar_id = created['id']

    with allure.step("Update calendar name"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "name": "Updated Name"
        })

    with allure.step("Verify name changed"):
        assert updated['id'] == calendar_id
        assert updated['name'] == "Updated Name"
        assert updated['name'] != created['name']


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_color(auth_client):
    """Update calendar color and verify change persists"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar",
            "color": "#ff5733"
        })
        calendar_id = created['id']

    with allure.step("Update calendar color"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "color": "#1a73e8"
        })

    with allure.step("Verify color changed"):
        assert updated['id'] == calendar_id
        assert updated['color'] == "#1a73e8"
        assert updated['color'] != created['color']


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_name_and_color_together(auth_client):
    """Update calendar name and color together and verify both change"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Original Name",
            "color": "#ff5733"
        })
        calendar_id = created['id']

    with allure.step("Update both name and color"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "name": "New Name",
            "color": "#1a73e8"
        })

    with allure.step("Verify both fields changed"):
        assert updated['id'] == calendar_id
        assert updated['name'] == "New Name"
        assert updated['color'] == "#1a73e8"
        assert updated['name'] != created['name']
        assert updated['color'] != created['color']


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_active_status_not_allowed(auth_client):
    """Update calendar active status via PATCH returns 400 - must use activate/deactivate endpoints"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })
        calendar_id = created['id']

    with allure.step("Attempt to update active field via PATCH"):
        response = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "active": False
        }, handle_response=False)

    with allure.step("Verify 400 response (active field not allowed)"):
        assert response.status_code == 400


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_with_empty_name(auth_client):
    """Update calendar with empty name returns 400"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Original Name"
        })
        calendar_id = created['id']

    with allure.step("Attempt to update with empty name"):
        response = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "name": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_with_no_data(auth_client):
    """Update calendar with no data returns 400 'No update data provided'"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })
        calendar_id = created['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.patch(f'/api/calendars/{calendar_id}', {},
                                   handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_with_external_uid(auth_client):
    """Update calendar with external_uid - verify field is read-only"""
    with allure.step("Create test calendar with external_uid"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar",
            "external_uid": "original-uid"
        })
        calendar_id = created['id']
        original_uid = created['external_uid']

    with allure.step("Attempt to update external_uid"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "external_uid": "new-uid"
        })

    with allure.step("Verify external_uid was not changed (read-only)"):
        assert updated['external_uid'] == original_uid
        assert updated['external_uid'] != "new-uid"


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_calendar_with_external_source(auth_client):
    """Update calendar with external_source - verify field is read-only"""
    with allure.step("Create test calendar with external_source"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar",
            "external_source": "caldav"
        })
        calendar_id = created['id']
        original_source = created['external_source']

    with allure.step("Attempt to update external_source"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "external_source": "different-source"
        })

    with allure.step("Verify external_source was not changed (read-only)"):
        assert updated['external_source'] == original_source
        assert updated['external_source'] != "different-source"


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_calendar(auth_client):
    """Update nonexistent calendar returns 404"""
    with allure.step("Attempt to update non-existent calendar"):
        response = auth_client.patch('/api/calendars/999999', {
            "name": "Updated Name"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Calendars')
@allure.story('Update Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_users_calendar(auth_client, secondary_auth_client):
    """Update another user's calendar returns 404"""
    with allure.step("Primary user creates calendar"):
        primary_cal = auth_client.post('/api/calendars', {
            "name": "Primary User Calendar"
        })
        primary_cal_id = primary_cal['id']

    with allure.step("Secondary user attempts to update primary user's calendar"):
        response = secondary_auth_client.patch(f'/api/calendars/{primary_cal_id}', {
            "name": "Hacked Name"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404