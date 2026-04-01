import pytest
import allure


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_title(auth_client):
    """Update routine title verifies change persists"""
    with allure.step("Create test routine"):
        created = auth_client.post('/api/routines', {
            "title": "Original Title"
        })
        routine_id = created['id']

    with allure.step("Update routine title"):
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "title": "Updated Title"
        })

    with allure.step("Verify title was updated"):
        assert updated['id'] == routine_id
        assert updated['title'] != created['title']
        assert updated['title'] == "Updated Title"


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_description(auth_client):
    """Update routine description verifies change persists"""
    with allure.step("Create routine with description"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "description": "Original description"
        })
        routine_id = created['id']

    with allure.step("Update routine description"):
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "description": "Updated description"
        })

    with allure.step("Verify description was updated"):
        assert updated['id'] == routine_id
        assert updated['description'] == "Updated description"
        assert updated['description'] != created['description']


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_rrule(auth_client):
    """Update routine rrule verifies change persists"""
    with allure.step("Create routine with RRULE"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "rrule": "FREQ=DAILY"
        })
        routine_id = created['id']

    with allure.step("Update routine RRULE"):
        new_rrule = "FREQ=WEEKLY;BYDAY=MO"
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "rrule": new_rrule
        })

    with allure.step("Verify RRULE was updated"):
        assert updated['id'] == routine_id
        assert updated['rrule'] == new_rrule
        assert updated['rrule'] != created['rrule']


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_start_time(auth_client):
    """Update routine start_time verifies change persists"""
    with allure.step("Create routine with start_time"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00"
        })
        routine_id = created['id']

    with allure.step("Update routine start_time"):
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "start_time": "10:00"
        })

    with allure.step("Verify start_time was updated"):
        assert updated['id'] == routine_id
        assert updated['start_time'] == "10:00"
        assert updated['start_time'] != created['start_time']


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_end_time(auth_client):
    """Update routine end_time verifies change persists"""
    with allure.step("Create routine with end_time"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "end_time": "17:00"
        })
        routine_id = created['id']

    with allure.step("Update routine end_time"):
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "end_time": "18:00"
        })

    with allure.step("Verify end_time was updated"):
        assert updated['id'] == routine_id
        assert updated['end_time'] == "18:00"
        assert updated['end_time'] != created['end_time']


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_active(auth_client):
    """Update routine active status verifies change persists"""
    with allure.step("Create active routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "active": True
        })
        routine_id = created['id']

    with allure.step("Update routine to inactive"):
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "active": False
        })

    with allure.step("Verify active status was updated"):
        assert updated['id'] == routine_id
        assert updated['active'] is False
        assert updated['active'] != created['active']


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_multiple_fields_together(auth_client):
    """Update multiple fields together (title, description, start_time)"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Original Title",
            "description": "Original description",
            "start_time": "09:00"
        })
        routine_id = created['id']

    with allure.step("Update multiple fields at once"):
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "title": "New Title",
            "description": "New description",
            "start_time": "10:00"
        })

    with allure.step("Verify all fields were updated"):
        assert updated['id'] == routine_id
        assert updated['title'] == "New Title"
        assert updated['description'] == "New description"
        assert updated['start_time'] == "10:00"


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_empty_title(auth_client):
    """Update routine with empty title returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Original Title"
        })
        routine_id = created['id']

    with allure.step("Attempt to update with empty title"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "title": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == "Title cannot be empty"


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_no_data(auth_client):
    """Update routine with no data returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update with no data"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {},
                                     handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == "No update data provided"



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_id(auth_client):
    """Update routine with disallowed field (id) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update id field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "id": 12345
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_user_id(auth_client):
    """Update routine with disallowed field (user_id) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update user_id field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "user_id": 99999
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_created_at(auth_client):
    """Update routine with disallowed field (created_at) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update created_at field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "created_at": "2026-01-01T00:00:00"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_updated_at(auth_client):
    """Update routine with disallowed field (updated_at) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update updated_at field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "updated_at": "2026-01-01T00:00:00"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_calendar_id(auth_client):
    """Update routine with disallowed field (calendar_id) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update calendar_id field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "calendar_id": 123
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_external_uid(auth_client):
    """Update routine with disallowed field (external_uid) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update external_uid field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "external_uid": "new-uid"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_external_source(auth_client):
    """Update routine with disallowed field (external_source) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update external_source field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "external_source": "new-source"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_disallowed_field_external_source_name(auth_client):
    """Update routine with disallowed field (external_source_name) returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Attempt to update external_source_name field"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "external_source_name": "New Source Name"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Cannot update read-only fields" in response.json['error']



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_invalid_rrule(auth_client):
    """Update routine with invalid RRULE returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "rrule": "FREQ=DAILY"
        })
        routine_id = created['id']

    with allure.step("Attempt to update with invalid RRULE"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "rrule": "INVALID_RRULE"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "invalid rrule" in response.json['error'].lower()


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_invalid_start_time(auth_client):
    """Update routine with invalid start_time returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "start_time": "09:00"
        })
        routine_id = created['id']

    with allure.step("Attempt to update with invalid start_time"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "start_time": "25:00"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == "start_time must be in HH:MM format"


@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_routine_with_invalid_end_time(auth_client):
    """Update routine with invalid end_time returns 400"""
    with allure.step("Create routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine",
            "end_time": "17:00"
        })
        routine_id = created['id']

    with allure.step("Attempt to update with invalid end_time"):
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "end_time": "invalid"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == "end_time must be in HH:MM format"



@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_routine(auth_client):
    """Update nonexistent routine returns 404"""
    with allure.step("Attempt to update nonexistent routine"):
        routine_id = 99999
        response = auth_client.patch(f'/api/routines/{routine_id}', {
            "title": "Updated Title"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert response.json['error'] == f"Routine {routine_id} not found"






@allure.feature('Routines')
@allure.story('Update Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_user_routine(auth_client, secondary_auth_client):
    """Update another user's routine returns 404"""
    with allure.step("Secondary user creates routine"):
        secondary_routine = secondary_auth_client.post('/api/routines', {
            "title": "Secondary User Routine"
        })
        secondary_routine_id = secondary_routine['id']

    with allure.step("Primary user attempts to update secondary user's routine"):
        response = auth_client.patch(f'/api/routines/{secondary_routine_id}', {
            "title": "Hijacked Title"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify error message"):
        assert response.json['error'] == f"Routine {secondary_routine_id} not found"
