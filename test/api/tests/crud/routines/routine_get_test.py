import pytest
import allure


@allure.feature('Routines')
@allure.story('Get Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_routine_returns_full_object(auth_client):
    """Get routine returns full object with all fields"""
    with allure.step("Create routine with multiple fields"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "description": "Test description",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00",
            "active": True
        })
        routine_id = created['id']

    with allure.step("Retrieve routine by ID"):
        routine = auth_client.get(f'/api/routines/{routine_id}')

    with allure.step("Verify all fields present"):
        assert routine['id'] == routine_id
        assert routine['title'] == "Test Routine"
        assert routine['description'] == "Test description"
        assert routine['rrule'] == "FREQ=DAILY"
        assert routine['start_time'] == "09:00"
        assert routine['end_time'] == "10:00"
        assert routine['active'] is True
        assert routine['user_id']
        assert isinstance(routine['user_id'], int)
        assert 'calendar_id' in routine
        assert 'external_uid' in routine
        assert 'external_source' in routine
        assert 'external_source_name' in routine
        assert 'tags' in routine
        assert isinstance(routine['tags'], list)
        assert 'principles' in routine
        assert isinstance(routine['principles'], list)
        assert 'created_at' in routine
        assert 'updated_at' in routine


@allure.feature('Routines')
@allure.story('Get Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_routine(auth_client):
    """Get nonexistent routine returns 404"""
    with allure.step("Attempt to retrieve nonexistent routine"):
        routine_id = 999999
        response = auth_client.get(f'/api/routines/{routine_id}',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert f"routine {routine_id} not found" in response.json['error'].lower()

@allure.feature('Routines')
@allure.story('Get Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.get
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_user_routine(auth_client, secondary_auth_client):
    """Get another user's routine returns 404"""
    with allure.step("Secondary user creates routine"):
        secondary_routine = secondary_auth_client.post('/api/routines', {
            "title": "Secondary User Routine"
        })
        routine_id = secondary_routine['id']

    with allure.step("Primary user attempts to retrieve secondary user's routine"):
        response = auth_client.get(f'/api/routines/{routine_id}',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert f"routine {routine_id} not found" in response.json['error'].lower()
