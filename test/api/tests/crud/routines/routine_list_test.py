import pytest
import allure


@allure.feature('Routines')
@allure.story('List Routines')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_routines_excludes_inactive_by_default(auth_client):
    """List routines excludes inactive by default"""
    with allure.step("Create active routine"):
        active_routine = auth_client.post('/api/routines', {
            "title": "Active Routine",
            "active": True
        })

    with allure.step("Create inactive routine"):
        inactive_routine = auth_client.post('/api/routines', {
            "title": "Inactive Routine",
            "active": False
        })

    with allure.step("List routines without parameters"):
        response = auth_client.get('/api/routines')
        routines = response.json

    with allure.step("Verify only active routine returned"):
        routine_ids = [routine['id'] for routine in routines]
        assert active_routine['id'] in routine_ids
        assert inactive_routine['id'] not in routine_ids


@allure.feature('Routines')
@allure.story('List Routines')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_routines_with_active_only_true(auth_client):
    """List routines with active_only=true excludes inactive routines"""
    with allure.step("Create active routine"):
        active_routine = auth_client.post('/api/routines', {
            "title": "Active Routine",
            "active": True
        })

    with allure.step("Create inactive routine"):
        inactive_routine = auth_client.post('/api/routines', {
            "title": "Inactive Routine",
            "active": False
        })

    with allure.step("List routines with active_only=true"):
        response = auth_client.get('/api/routines', params={'active_only': True})
        routines = response.json

    with allure.step("Verify only active routine returned"):
        routine_ids = [routine['id'] for routine in routines]
        assert active_routine['id'] in routine_ids
        assert inactive_routine['id'] not in routine_ids


@allure.feature('Routines')
@allure.story('List Routines')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_routines_with_active_only_false(auth_client):
    """List routines with active_only=false includes inactive routines"""
    with allure.step("Create active routine"):
        active_routine = auth_client.post('/api/routines', {
            "title": "Active Routine",
            "active": True
        })

    with allure.step("Create inactive routine"):
        inactive_routine = auth_client.post('/api/routines', {
            "title": "Inactive Routine",
            "active": False
        })

    with allure.step("List routines with active_only=false"):
        response = auth_client.get('/api/routines', params={'active_only': False})
        routines = response.json

    with allure.step("Verify both active and inactive routines returned"):
        routine_ids = [routine['id'] for routine in routines]
        assert active_routine['id'] in routine_ids
        assert inactive_routine['id'] in routine_ids


@allure.feature('Routines')
@allure.story('List Routines')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_routines_returns_empty_array(auth_client):
    """List routines returns empty array for user with no routines"""
    with allure.step("List routines for new user"):
        response = auth_client.get('/api/routines')
        routines = response.json

    with allure.step("Verify empty array returned"):
        assert isinstance(routines, list)
        assert len(routines) == 0


@allure.feature('Routines')
@allure.story('List Routines')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.list
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_list_routines_only_returns_user_own_routines(auth_client, secondary_auth_client):
    """List routines only returns user's own routines (isolation test)"""
    with allure.step("Primary user creates routine"):
        primary_routine = auth_client.post('/api/routines', {
            "title": "Primary User Routine"
        })

    with allure.step("Secondary user creates routine"):
        secondary_routine = secondary_auth_client.post('/api/routines', {
            "title": "Secondary User Routine"
        })

    with allure.step("Primary user lists their routines"):
        primary_response = auth_client.get('/api/routines')
        primary_routines = primary_response.json
        primary_ids = [routine['id'] for routine in primary_routines]

    with allure.step("Secondary user lists their routines"):
        secondary_response = secondary_auth_client.get('/api/routines')
        secondary_routines = secondary_response.json
        secondary_ids = [routine['id'] for routine in secondary_routines]

    with allure.step("Verify user isolation"):
        assert primary_routine['id'] in primary_ids
        assert primary_routine['id'] not in secondary_ids
        assert secondary_routine['id'] in secondary_ids
        assert secondary_routine['id'] not in primary_ids