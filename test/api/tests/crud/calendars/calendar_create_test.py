import pytest
import allure


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_all_fields(auth_client):
    """Create calendar with all available fields populated"""
    with allure.step("Create calendar with all fields"):
        response = auth_client.post('/api/calendars', {
            "name": "Complete Calendar",
            "color": "#ff5733"
        })

    with allure.step("Verify all fields are set correctly"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['name'] == "Complete Calendar"
        assert response['color'] == "#ff5733"
        assert response['active'] is True
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_verifies_defaults(auth_client):
    """Create calendar verifies defaults (active=true, color=#767676)"""
    with allure.step("Create calendar with only name"):
        response = auth_client.post('/api/calendars', {
            "name": "Calendar with defaults"
        })

    with allure.step("Verify default values"):
        assert response['active'] is True, "active should default to true"
        assert response['color'] == "#767676", "color should default to #767676"
        assert response['external_uid'] is None, "external_uid should be null for local calendars"
        assert response['external_source'] is None, "external_source should be null for local calendars"


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_custom_color(auth_client):
    """Create calendar with custom color"""
    with allure.step("Create calendar with custom color"):
        response = auth_client.post('/api/calendars', {
            "name": "Colorful Calendar",
            "color": "#1a73e8"
        })

    with allure.step("Verify color is set correctly"):
        assert response['color'] == "#1a73e8"
        assert response['id']


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_without_name(auth_client):
    """Create calendar without name returns 400"""
    with allure.step("Attempt to create calendar without name"):
        response = auth_client.post('/api/calendars', {
            "color": "#ff5733"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Calendar name is required"


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_empty_name(auth_client):
    """Create calendar with empty name returns 400"""
    with allure.step("Attempt to create calendar with empty name"):
        response = auth_client.post('/api/calendars', {
            "name": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Calendar name cannot be empty"

@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_whitespace_only_name(auth_client):
    """Create calendar with whitespace-only name returns 400"""
    with allure.step("Attempt to create calendar with whitespace-only name"):
        response = auth_client.post('/api/calendars', {
            "name": "   "
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Calendar name cannot be empty"


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_name_exactly_200_chars(auth_client):
    """Create calendar with name exactly 200 characters succeeds (boundary test)"""
    with allure.step("Create calendar with 200-character name"):
        name_200_chars = "A" * 200
        response = auth_client.post('/api/calendars', {
            "name": name_200_chars
        })

    with allure.step("Verify calendar created successfully"):
        assert response['id']
        assert response['name'] == name_200_chars
        assert len(response['name']) == 200


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_name_over_200_chars(auth_client):
    """Create calendar with name over 200 characters returns 400 (boundary test)"""
    with allure.step("Attempt to create calendar with 201-character name"):
        name_201_chars = "A" * 201
        response = auth_client.post('/api/calendars', {
            "name": name_201_chars
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Calendar name cannot exceed 200 characters"


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_empty_request_body(auth_client):
    """Create calendar with empty request body returns 400"""
    with allure.step("Attempt to create calendar with empty body"):
        response = auth_client.post('/api/calendars', {}, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response['error'] == "Request body is required"


@allure.feature('Calendars')
@allure.story('Create Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_calendar_with_invalid_color_format(auth_client):
    """Create calendar with invalid color format returns validation error"""
    with allure.step("Attempt to create calendar with invalid color"):
        response = auth_client.post('/api/calendars', {
            "name": "Invalid Color Calendar",
            "color": "red"  # Should be hex format like #ff0000
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Color must be in hex format" in response['error']

