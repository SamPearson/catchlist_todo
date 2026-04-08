import pytest
import allure


@allure.feature('Calendars')
@allure.story('Calendar Deactivation')
@pytest.mark.calendars
@pytest.mark.activation_status
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_calendar_with_cascade_true(auth_client):
    """Deactivate calendar with cascade=true (default) - routines are deactivated"""
    with allure.step("Create calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })
        calendar_id = calendar['id']

    with allure.step("Create 2 active routines in the calendar"):
        routine1 = auth_client.post('/api/routines', {
            "title": "Active Routine 1",
            "calendar_id": calendar_id,
            "active": True
        })
        routine1_id = routine1['id']

        routine2 = auth_client.post('/api/routines', {
            "title": "Active Routine 2",
            "calendar_id": calendar_id,
            "active": True
        })
        routine2_id = routine2['id']

    with allure.step("Deactivate calendar (default cascade=true)"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}/deactivate',
                                  params = {'cascade': 'true'})

    with allure.step("Verify calendar is deactivated"):
        assert updated['active'] is False

    with allure.step("Verify both routines are deactivated"):
        routine1_check = auth_client.get(f'/api/routines/{routine1_id}')
        assert routine1_check['active'] is False

        routine2_check = auth_client.get(f'/api/routines/{routine2_id}')
        assert routine2_check['active'] is False


@allure.feature('Calendars')
@allure.story('Calendar Deactivation')
@pytest.mark.calendars
@pytest.mark.activation_status
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_calendar_with_cascade_false(auth_client):
    """Deactivate calendar with cascade=false - routines remain active"""
    with allure.step("Create calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })
        calendar_id = calendar['id']

    with allure.step("Create 2 active routines in the calendar"):
        routine1 = auth_client.post('/api/routines', {
            "title": "Active Routine 1",
            "calendar_id": calendar_id,
            "active": True
        })
        routine1_id = routine1['id']

        routine2 = auth_client.post('/api/routines', {
            "title": "Active Routine 2",
            "calendar_id": calendar_id,
            "active": True
        })
        routine2_id = routine2['id']

    with allure.step("Deactivate calendar with cascade=false"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}/deactivate',
                                  params={'cascade': 'false'})

    with allure.step("Verify calendar is deactivated"):
        assert updated['active'] is False

    with allure.step("Verify both routines remain active"):
        routine1_check = auth_client.get(f'/api/routines/{routine1_id}')
        assert routine1_check['active'] is True

        routine2_check = auth_client.get(f'/api/routines/{routine2_id}')
        assert routine2_check['active'] is True


@allure.feature('Calendars')
@allure.story('Calendar Deactivation')
@pytest.mark.calendars
@pytest.mark.activation_status
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_calendar_without_cascade_parameter(auth_client):
    """Deactivate calendar without cascade parameter - verify default behavior (cascade=true)"""
    with allure.step("Create calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })
        calendar_id = calendar['id']

    with allure.step("Create 2 active routines in the calendar"):
        routine1 = auth_client.post('/api/routines', {
            "title": "Active Routine 1",
            "calendar_id": calendar_id,
            "active": True
        })
        routine1_id = routine1['id']

        routine2 = auth_client.post('/api/routines', {
            "title": "Active Routine 2",
            "calendar_id": calendar_id,
            "active": True
        })
        routine2_id = routine2['id']

    with allure.step("Deactivate calendar without cascade parameter"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}/deactivate')

    with allure.step("Verify calendar is deactivated"):
        assert updated['active'] is False

    with allure.step("Verify both routines are deactivated (default cascade behavior)"):
        routine1_check = auth_client.get(f'/api/routines/{routine1_id}')
        assert routine1_check['active'] is False

        routine2_check = auth_client.get(f'/api/routines/{routine2_id}')
        assert routine2_check['active'] is False


@allure.feature('Calendars')
@allure.story('Calendar Activation Status')
@pytest.mark.calendars
@pytest.mark.activation_status
@allure.severity(allure.severity_level.NORMAL)
def test_activate_calendar_with_cascade_true(auth_client):
    """Activate calendar with cascade=true (default) - routines are activated"""
    with allure.step("Create inactive calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Test Calendar",
            "active": False
        })
        calendar_id = calendar['id']

    with allure.step("Create 2 inactive routines in the calendar"):
        routine1 = auth_client.post('/api/routines', {
            "title": "Inactive Routine 1",
            "calendar_id": calendar_id,
            "active": False
        })
        routine1_id = routine1['id']

        routine2 = auth_client.post('/api/routines', {
            "title": "Inactive Routine 2",
            "calendar_id": calendar_id,
            "active": False
        })
        routine2_id = routine2['id']

    with allure.step("Activate calendar (default cascade=true)"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}/activate',
                                  params = {'cascade': 'true'})

    with allure.step("Verify calendar is Activated"):
        assert updated['active'] is True

    with allure.step("Verify both routines are Activated"):
        routine1_check = auth_client.get(f'/api/routines/{routine1_id}')
        assert routine1_check['active'] is True

        routine2_check = auth_client.get(f'/api/routines/{routine2_id}')
        assert routine2_check['active'] is True


@allure.feature('Calendars')
@allure.story('Calendar Deactivation')
@pytest.mark.calendars
@pytest.mark.activation_status
@allure.severity(allure.severity_level.NORMAL)
def test_activate_calendar_with_cascade_false(auth_client):
    """Activate calendar with cascade=false - routines remain inactive"""
    with allure.step("Create Inactive calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Test Calendar",
            "active": False
        })
        calendar_id = calendar['id']

    with allure.step("Create 2 inactive routines in the calendar"):
        routine1 = auth_client.post('/api/routines', {
            "title": "Inactive Routine 1",
            "calendar_id": calendar_id,
            "active": False
        })
        routine1_id = routine1['id']

        routine2 = auth_client.post('/api/routines', {
            "title": "Inactive Routine 2",
            "calendar_id": calendar_id,
            "active": False
        })
        routine2_id = routine2['id']

    with allure.step("Activate calendar with cascade=false"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}/activate',
                                  params={'cascade': 'false'})

    with allure.step("Verify calendar is deactivated"):
        assert updated['active'] is True

    with allure.step("Verify both routines remain inactive"):
        routine1_check = auth_client.get(f'/api/routines/{routine1_id}')
        assert routine1_check['active'] is False

        routine2_check = auth_client.get(f'/api/routines/{routine2_id}')
        assert routine2_check['active'] is False


@allure.feature('Calendars')
@allure.story('Calendar Deactivation')
@pytest.mark.calendars
@pytest.mark.activation_status
@allure.severity(allure.severity_level.NORMAL)
def test_activate_calendar_without_cascade_parameter(auth_client):
    """Activate calendar without cascade parameter - verify default behavior (cascade=true)"""
    with allure.step("Create inactive calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Test Calendar",
            "active": False
        })
        calendar_id = calendar['id']

    with allure.step("Create 2 inactive routines in the calendar"):
        routine1 = auth_client.post('/api/routines', {
            "title": "Inactive Routine 1",
            "calendar_id": calendar_id,
            "active": False
        })
        routine1_id = routine1['id']

        routine2 = auth_client.post('/api/routines', {
            "title": "Inactive Routine 2",
            "calendar_id": calendar_id,
            "active": False
        })
        routine2_id = routine2['id']

    with allure.step("Activate calendar without cascade parameter"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}/activate')

    with allure.step("Verify calendar is Activated"):
        assert updated['active'] is True

    with allure.step("Verify both routines are Activated"):
        routine1_check = auth_client.get(f'/api/routines/{routine1_id}')
        assert routine1_check['active'] is True

        routine2_check = auth_client.get(f'/api/routines/{routine2_id}')
        assert routine2_check['active'] is True




