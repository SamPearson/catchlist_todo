import pytest
import allure


@allure.feature('Calendars')
@allure.story('Delete Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_calendar(auth_client):
    """Delete calendar returns 204 No Content"""
    with allure.step("Create test calendar"):
        created = auth_client.post('/api/calendars', {
            "name": "Calendar to Delete"
        })
        calendar_id = created['id']

    with allure.step("Delete calendar"):
        response = auth_client.delete(f'/api/calendars/{calendar_id}',
                                      handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204
        assert response.json is None

    with allure.step("Verify calendar no longer exists"):
        response = auth_client.get(f'/api/calendars/{calendar_id}',
                                   handle_response=False)
        assert response.status_code == 404
        assert response['error'] == "Calendar not found"



@allure.feature('Calendars')
@allure.story('Delete Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_calendar_with_routines_cascade(auth_client):
    """Delete calendar with routines - verify all routines are deleted (cascade)"""
    with allure.step("Create test calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Calendar with Routines"
        })
        calendar_id = calendar['id']

    with allure.step("Create 2 routines in the calendar"):
        routine1 = auth_client.post('/api/routines', {
            "title": "Routine 1",
            "calendar_id": calendar_id
        })
        routine1_id = routine1['id']

        routine2 = auth_client.post('/api/routines', {
            "title": "Routine 2",
            "calendar_id": calendar_id
        })
        routine2_id = routine2['id']

    with allure.step("Delete calendar"):
        auth_client.delete(f'/api/calendars/{calendar_id}',
                          handle_response=False)

    with allure.step("Verify calendar is deleted"):
        cal_response = auth_client.get(f'/api/calendars/{calendar_id}',
                                       handle_response=False)
        assert cal_response.status_code == 404

    with allure.step("Verify both routines are deleted"):
        routine1_response = auth_client.get(f'/api/routines/{routine1_id}',
                                            handle_response=False)
        assert routine1_response.status_code == 404

        routine2_response = auth_client.get(f'/api/routines/{routine2_id}',
                                            handle_response=False)
        assert routine2_response.status_code == 404


@allure.feature('Calendars')
@allure.story('Delete Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_calendar(auth_client):
    """Delete nonexistent calendar returns 404"""
    with allure.step("Attempt to delete non-existent calendar"):
        response = auth_client.delete('/api/calendars/999999',
                                      handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404
        assert response['error'] == "Calendar not found"


@allure.feature('Calendars')
@allure.story('Delete Calendar')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_users_calendar(auth_client, secondary_auth_client):
    """Delete another user's calendar returns 404"""
    with allure.step("Primary user creates calendar"):
        primary_cal = auth_client.post('/api/calendars', {
            "name": "Primary User Calendar"
        })
        primary_cal_id = primary_cal['id']

    with allure.step("Secondary user attempts to delete primary user's calendar"):
        response = secondary_auth_client.delete(f'/api/calendars/{primary_cal_id}',
                                                handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404
        assert response['error'] == "Calendar not found"

    with allure.step("Verify calendar still exists for primary user"):
        calendar = auth_client.get(f'/api/calendars/{primary_cal_id}')
        assert calendar['id'] == primary_cal_id