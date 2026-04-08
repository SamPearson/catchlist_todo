import pytest
import allure


@allure.feature('Calendars')
@allure.story('CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_basic_calendar(auth_client):
    """Create a basic calendar with only name"""
    with allure.step("Create calendar with only required field"):
        response = auth_client.post('/api/calendars', {
            "name": "Basic Calendar"
        })

    with allure.step("Verify calendar created successfully"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['name'] == "Basic Calendar"
        assert response['active'] is True
        assert response['color'] == "#767676"  # Default color


@allure.feature('Calendars')
@allure.story('CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_calendars(auth_client):
    """List calendars verifies calendar appears"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })
        calendar_id = created['id']

    with allure.step("List all calendars"):
        response = auth_client.get('/api/calendars')
        calendars = response.json

    with allure.step("Verify created calendar appears in list"):
        assert isinstance(calendars, list)
        calendar_ids = [cal['id'] for cal in calendars]
        assert calendar_id in calendar_ids


@allure.feature('Calendars')
@allure.story('CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_calendar_by_id(auth_client):
    """Get calendar by ID returns full calendar object"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })
        calendar_id = created['id']

    with allure.step("Retrieve calendar by ID"):
        calendar = auth_client.get(f'/api/calendars/{calendar_id}')

    with allure.step("Verify calendar data"):
        assert calendar['id'] == calendar_id
        assert calendar['name'] == "Test Calendar"
        assert calendar['user_id']
        assert 'created_at' in calendar
        assert 'updated_at' in calendar


@allure.feature('Calendars')
@allure.story('CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_calendar_name(auth_client):
    """Update calendar name"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Original Name"
        })
        calendar_id = created['id']

    with allure.step("Update calendar name"):
        updated = auth_client.patch(f'/api/calendars/{calendar_id}', {
            "name": "Updated Name"
        })

    with allure.step("Verify name was updated"):
        assert updated['id'] == calendar_id
        assert updated['name'] == "Updated Name"
        assert updated['name'] != created['name']


@allure.feature('Calendars')
@allure.story('CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_calendar(auth_client):
    """Delete calendar removes it from the system"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Calendar to Delete"
        })
        calendar_id = created['id']

    with allure.step("Delete calendar"):
        response = auth_client.delete(f'/api/calendars/{calendar_id}',
                                      handle_response=False)

    with allure.step("Verify 204 No Content response"):
        assert response.status_code == 204

    with allure.step("Verify calendar no longer exists"):
        get_response = auth_client.get(f'/api/calendars/{calendar_id}',
                                       handle_response=False)
        assert get_response.status_code == 404