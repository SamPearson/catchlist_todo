import pytest
import allure


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_all_fields(auth_client):
    """Create routine with all available fields populated"""
    with allure.step("Create calendar for routine"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Test Calendar"
        })

    with allure.step("Create routine with all fields"):
        response = auth_client.post('/api/routines', {
            "title": "Complete Routine",
            "description": "Full routine description",
            "rrule": "FREQ=DAILY",
            "start_time": "09:00",
            "end_time": "10:00",
            "active": True,
            "calendar_id": calendar['id']
        })

    with allure.step("Verify all fields are set correctly"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['title'] == "Complete Routine"
        assert response['description'] == "Full routine description"
        assert response['rrule'] == "FREQ=DAILY"
        assert response['start_time'] == "09:00"
        assert response['end_time'] == "10:00"
        assert response['active'] is True
        assert response['calendar_id'] == calendar['id']



@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_verifies_defaults(auth_client):
    """Create routine verifies defaults (active=true)"""
    with allure.step("Create routine with only title"):
        response = auth_client.post('/api/routines', {
            "title": "Routine with defaults"
        })

    with allure.step("Verify default values"):
        assert response['active'] is True, "active should default to true"
        assert response['description'] is None, "description should be null when not provided"
        assert response['rrule'] is None, "rrule should be null for ad-hoc routines"
        assert response['start_time'] is None, "start_time should be null when not provided"
        assert response['end_time'] is None, "end_time should be null when not provided"
        assert response['calendar_id'] is None, "calendar_id should be null for standalone routines"
        assert response['external_uid'] is None, "external_uid should be null for local routines"
        assert response['external_source'] is None, "external_source should be null for local routines"
        assert response['external_source_name'] is None, "external_source_name should be null for local routines"


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_active_false(auth_client):
    """Create routine with active=false"""
    with allure.step("Create inactive routine"):
        response = auth_client.post('/api/routines', {
            "title": "Inactive Routine",
            "active": False
        })

    with allure.step("Verify routine is inactive"):
        assert response['id']
        assert response['active'] is False


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_rrule_daily(auth_client):
    """Create routine with RRULE (FREQ=DAILY)"""
    with allure.step("Create routine with daily recurrence"):
        response = auth_client.post('/api/routines', {
            "title": "Daily Routine",
            "rrule": "FREQ=DAILY"
        })

    with allure.step("Verify RRULE stored correctly"):
        assert response['id']
        assert response['rrule'] == "FREQ=DAILY"


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_rrule_weekly_single_day(auth_client):
    """Create routine with RRULE (FREQ=WEEKLY;BYDAY=MO)"""
    with allure.step("Create routine with weekly Monday recurrence"):
        response = auth_client.post('/api/routines', {
            "title": "Monday Routine",
            "rrule": "FREQ=WEEKLY;BYDAY=MO"
        })

    with allure.step("Verify complex RRULE stored correctly"):
        assert response['id']
        assert response['rrule'] == "FREQ=WEEKLY;BYDAY=MO"


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_rrule_weekly_multiple_days(auth_client):
    """Create routine with RRULE (FREQ=WEEKLY;BYDAY=MO,WE,FR)"""
    with allure.step("Create routine with multi-day weekly recurrence"):
        response = auth_client.post('/api/routines', {
            "title": "MWF Routine",
            "rrule": "FREQ=WEEKLY;BYDAY=MO,WE,FR"
        })

    with allure.step("Verify multi-day RRULE stored correctly"):
        assert response['id']
        assert response['rrule'] == "FREQ=WEEKLY;BYDAY=MO,WE,FR"


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_without_rrule(auth_client):
    """Create routine without RRULE (ad-hoc routine for manual session tracking)"""
    with allure.step("Create ad-hoc routine"):
        response = auth_client.post('/api/routines', {
            "title": "Ad-hoc Activity"
        })

    with allure.step("Verify routine created without RRULE"):
        assert response['id']
        assert response['rrule'] is None
        assert response['title'] == "Ad-hoc Activity"


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_start_time_only(auth_client):
    """Create routine with start_time only (end_time is optional)"""
    with allure.step("Create routine with only start_time"):
        response = auth_client.post('/api/routines', {
            "title": "Morning Routine",
            "start_time": "07:00"
        })

    with allure.step("Verify start_time set and end_time null"):
        assert response['id']
        assert response['start_time'] == "07:00"
        assert response['end_time'] is None


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_end_time_only(auth_client):
    """Create routine with end_time only (start_time is optional)"""
    with allure.step("Create routine with only end_time"):
        response = auth_client.post('/api/routines', {
            "title": "Evening Routine",
            "end_time": "22:00"
        })

    with allure.step("Verify end_time set and start_time null"):
        assert response['id']
        assert response['start_time'] is None
        assert response['end_time'] == "22:00"


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_start_and_end_time(auth_client):
    """Create routine with both start_time and end_time"""
    with allure.step("Create routine with start and end times"):
        response = auth_client.post('/api/routines', {
            "title": "Timed Routine",
            "start_time": "14:00",
            "end_time": "15:30"
        })

    with allure.step("Verify both times stored correctly"):
        assert response['id']
        assert response['start_time'] == "14:00"
        assert response['end_time'] == "15:30"


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_calendar_id(auth_client):
    """Create routine with calendar_id (calendar association)"""
    with allure.step("Create test calendar"):
        calendar = auth_client.post('/api/calendars', {
            "name": "Workout Calendar"
        })

    with allure.step("Create routine associated with calendar"):
        response = auth_client.post('/api/routines', {
            "title": "Leg Day",
            "calendar_id": calendar['id']
        })

    with allure.step("Verify calendar association"):
        assert response['id']
        assert response['calendar_id'] == calendar['id']


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_external_fields(auth_client):
    """Cannot directly create routine with external fields (external_uid, external_source, external_source_name)"""
    with allure.step("Create routine with external metadata"):
        response = auth_client.post('/api/routines', {
            "title": "Imported Routine",
            "external_uid": "abc-123-def-456",
            "external_source": "caldav",
            "external_source_name": "Google Calendar"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        error_message = "Cannot set external_uid, external_source or external_source_name manually"
        assert error_message in response.json['error']


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_without_title(auth_client):
    """Create routine without title returns 400"""
    with allure.step("Attempt to create routine without title"):
        response = auth_client.post('/api/routines', {
            "description": "Routine without title"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Title is required" in response.json['error']


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_empty_title(auth_client):
    """Create routine with empty title returns 400"""
    with allure.step("Attempt to create routine with empty title"):
        response = auth_client.post('/api/routines', {
            "title": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Title is required" in response.json['error']



@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_whitespace_only_title(auth_client):
    """Create routine with whitespace-only title returns 400"""
    with allure.step("Attempt to create routine with whitespace-only title"):
        response = auth_client.post('/api/routines', {
            "title": "   "
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Title cannot be empty" in response.json['error']


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_title_exactly_200_chars(auth_client):
    """Create routine with title exactly 200 characters succeeds (boundary test)"""
    with allure.step("Create routine with 200-character title"):
        title_200_chars = "A" * 200
        response = auth_client.post('/api/routines', {
            "title": title_200_chars
        })

    with allure.step("Verify routine created successfully"):
        assert response['id']
        assert response['title'] == title_200_chars
        assert len(response['title']) == 200


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_title_over_200_chars(auth_client):
    """Create routine with title over 200 characters returns 400 (boundary test)"""
    with allure.step("Attempt to create routine with 201-character title"):
        title_201_chars = "A" * 201
        response = auth_client.post('/api/routines', {
            "title": title_201_chars
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "Title cannot exceed 200 characters" in response.json['error']


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_invalid_rrule_format(auth_client):
    """Create routine with invalid RRULE format returns 400"""
    with allure.step("Attempt to create routine with invalid RRULE"):
        response = auth_client.post('/api/routines', {
            "title": "Invalid RRULE Routine",
            "rrule": "INVALID_RRULE_FORMAT"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "invalid rrule" in response.json['error'].lower()


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_invalid_start_time_format(auth_client):
    """Create routine with invalid start_time format returns 400"""
    with allure.step("Attempt to create routine with invalid start_time"):
        response = auth_client.post('/api/routines', {
            "title": "Invalid Time Routine",
            "start_time": "25:00"  # Invalid hour
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "start_time must be in HH:MM format" in response.json['error']


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_invalid_end_time_format(auth_client):
    """Create routine with invalid end_time format returns 400"""
    with allure.step("Attempt to create routine with invalid end_time"):
        response = auth_client.post('/api/routines', {
            "title": "Invalid End Time Routine",
            "end_time": "invalid"
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert "end_time must be in HH:MM format" in response.json['error']



@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_empty_request_body(auth_client):
    """Create routine with empty request body returns 400"""
    with allure.step("Attempt to create routine with empty body"):
        response = auth_client.post('/api/routines', {}, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_nonexistent_calendar_id(auth_client):
    """Create routine with nonexistent calendar_id returns 404"""
    with allure.step("Attempt to create routine with nonexistent calendar"):
        response = auth_client.post('/api/routines', {
            "title": "Routine with bad calendar",
            "calendar_id": 999999
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == "Calendar 999999 not found."


@allure.feature('Routines')
@allure.story('Create Routine')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.create
@pytest.mark.auth
@allure.severity(allure.severity_level.NORMAL)
def test_create_routine_with_another_user_calendar_id(auth_client, secondary_auth_client):
    """Create routine with another user's calendar_id returns 404"""
    with allure.step("Secondary user creates calendar"):
        secondary_calendar = secondary_auth_client.post('/api/calendars', {
            "name": "Secondary User Calendar"
        })

    with allure.step("Primary user attempts to create routine with secondary user's calendar"):
        response = auth_client.post('/api/routines', {
            "title": "Unauthorized Calendar Routine",
            "calendar_id": secondary_calendar['id']
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400

    with allure.step("Verify error message"):
        assert response.json['error'] == f"Calendar {secondary_calendar['id']} not found."
