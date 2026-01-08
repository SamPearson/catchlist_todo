
import pytest
import allure


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_routine_with_required_fields(auth_client):
	"""Create routine with only required field (title)"""
	with allure.step("Prepare test data"):
		data = {"title": "Morning Routine"}

	with allure.step("Create new routine"):
		response = auth_client.post('/api/routines', data)

	with allure.step("Verify response structure and values"):
		# Response contains ID and timestamps
		assert response['id']
		assert isinstance(response['id'], int)

		# Title matches input
		assert response['title'] == data['title']
		assert isinstance(response['title'], str)

		# Active defaults to True
		assert response['active'] is True
		assert isinstance(response['active'], bool)

		# Timestamps present
		assert response['created_at']
		assert response['updated_at']
		assert isinstance(response['created_at'], str)
		assert isinstance(response['updated_at'], str)

		# Optional fields present but null/empty
		assert response['description'] is None
		assert response['rrule'] is None
		assert response['start_time'] is None
		assert response['end_time'] is None
		assert response['external_uid'] is None
		assert response['external_source'] is None
		assert response['calendar_id'] is None

		# Array fields present and empty
		assert response['tags'] == []
		assert response['principles'] == []


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_routine_with_description(auth_client):
	"""Create routine with title and description"""
	with allure.step("Prepare test data"):
		data = {
			"title": "Exercise Routine",
			"description": "Morning workout with cardio and weights"
		}

	with allure.step("Create new routine"):
		response = auth_client.post('/api/routines', data)

	with allure.step("Verify description is stored"):
		assert response['description'] == data['description']
		assert isinstance(response['description'], str)


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_routine_with_times(auth_client):
	"""Create routine with start and end times"""
	with allure.step("Prepare test data"):
		data = {
			"title": "Morning Standup",
			"start_time": "09:00",
			"end_time": "09:30"
		}

	with allure.step("Create new routine"):
		response = auth_client.post('/api/routines', data)

	with allure.step("Verify times are stored in HH:MM format"):
		assert response['start_time'] == "09:00"
		assert response['end_time'] == "09:30"


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_routine_with_rrule(auth_client):
	"""Create routine with recurrence rule"""
	with allure.step("Prepare test data"):
		data = {
			"title": "Weekly Team Meeting",
			"rrule": "FREQ=WEEKLY;BYDAY=MO",
			"start_time": "10:00",
			"end_time": "11:00"
		}

	with allure.step("Create new routine"):
		response = auth_client.post('/api/routines', data)

	with allure.step("Verify rrule is stored"):
		assert response['rrule'] == data['rrule']
		assert response['start_time'] == "10:00"
		assert response['end_time'] == "11:00"


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_create_routine_with_all_fields(auth_client):
	"""Create routine with all optional fields"""
	with allure.step("Create a calendar to attach"):
		calendar = auth_client.post('/api/calendars', {"name": "Test Calendar"})
		calendar_id = calendar['id']

	with allure.step("Prepare routine data"):
		data = {
			"title": "Complete Routine",
			"description": "A fully configured routine",
			"rrule": "FREQ=DAILY",
			"start_time": "06:00",
			"end_time": "07:00",
			"active": True,
			"calendar_id": calendar_id
		}

	with allure.step("Create new routine"):
		response = auth_client.post('/api/routines', data)

	with allure.step("Verify all fields are stored"):
		assert response['title'] == data['title']
		assert response['description'] == data['description']
		assert response['rrule'] == data['rrule']
		assert response['start_time'] == "06:00"
		assert response['end_time'] == "07:00"
		assert response['active'] is True
		assert response['calendar_id'] == calendar_id



@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_create_routine_invalid_end_time_format(auth_client):
	"""Create routine with invalid end_time format"""
	with allure.step("Prepare invalid time data"):
		data = {
			"title": "Bad Time Routine",
			"start_time": "09:00",
			"end_time": "25:00"  # Invalid hour
		}

	with allure.step("Attempt to create routine"):
		response = auth_client.post('/api/routines', data, handle_response=False)

	with allure.step("Verify error response"):
		assert response.status_code == 400


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_create_routine_missing_title(auth_client):
	"""Create routine without required title"""
	with allure.step("Prepare data without title"):
		data = {"description": "No title here"}

	with allure.step("Attempt to create routine"):
		response = auth_client.post('/api/routines', data, handle_response=False)

	with allure.step("Verify error response"):
		assert response.status_code == 400
		error = response.json()
		assert 'error' in error


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_multiple_routines(auth_client):
	"""Create multiple routines to verify independence"""
	with allure.step("Create first routine"):
		routine1 = auth_client.post('/api/routines', {"title": "Routine 1"})
		routine1_id = routine1['id']

	with allure.step("Create second routine"):
		routine2 = auth_client.post('/api/routines', {"title": "Routine 2"})
		routine2_id = routine2['id']

	with allure.step("Verify routines are independent"):
		assert routine1_id != routine2_id
		assert routine1['title'] != routine2['title']
		assert routine1['created_at'] <= routine2['created_at']


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_routines_returns_list(auth_client):
	"""Retrieve all routines for authenticated user"""
	with allure.step("Create multiple test routines"):
		created_ids = []
		for i in range(3):
			routine = auth_client.post('/api/routines', {
				"title": f"Test routine {i+1}"
			})
			created_ids.append(routine['id'])

	with allure.step("Retrieve all routines"):
		response = auth_client.get('/api/routines')

	with allure.step("Verify response structure"):
		assert isinstance(response, list)
		assert len(response) >= 3

		# Verify each routine has required fields
		for routine in response:
			assert routine['id']
			assert routine['title']
			assert 'active' in routine
			assert 'created_at' in routine
			assert 'updated_at' in routine
			assert 'tags' in routine
			assert 'principles' in routine

	with allure.step("Verify created routines are in list"):
		retrieved_ids = [r['id'] for r in response]
		for created_id in created_ids:
			assert created_id in retrieved_ids


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_routines_exclude_inactive_by_default(auth_client):
	"""List routines filters out inactive routines by default"""
	with allure.step("Create active routine"):
		active_routine = auth_client.post('/api/routines', {
			"title": "Active routine"
		})
		active_id = active_routine['id']

	with allure.step("Create and deactivate a routine"):
		inactive_routine = auth_client.post('/api/routines', {
			"title": "Inactive routine"
		})
		inactive_id = inactive_routine['id']
		auth_client.put(f'/api/routines/{inactive_id}', {
			"active": False
		})

	with allure.step("Retrieve all routines without filter"):
		response = auth_client.get('/api/routines')

	with allure.step("Verify inactive routine is excluded"):
		retrieved_ids = [r['id'] for r in response]
		assert active_id in retrieved_ids
		assert inactive_id not in retrieved_ids


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_routines_with_active_only_false(auth_client):
	"""List routines with active_only=false returns inactive routines"""
	with allure.step("Create and deactivate a routine"):
		inactive_routine = auth_client.post('/api/routines', {
			"title": "Inactive routine"
		})
		inactive_id = inactive_routine['id']
		auth_client.put(f'/api/routines/{inactive_id}', {
			"active": False
		})

	with allure.step("Retrieve all routines with active_only=false"):
		response = auth_client.get('/api/routines?active_only=false')

	with allure.step("Verify inactive routine is included"):
		retrieved_ids = [r['id'] for r in response]
		assert inactive_id in retrieved_ids


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_routine_by_id(auth_client):
	"""Retrieve a specific routine by ID"""
	with allure.step("Create test routine"):
		created = auth_client.post('/api/routines', {
			"title": "Routine for retrieval",
			"description": "Test description",
			"start_time": "08:00",
			"end_time": "09:00"
		})
		routine_id = created['id']

	with allure.step("Retrieve the routine"):
		retrieved = auth_client.get(f'/api/routines/{routine_id}')

	with allure.step("Verify retrieved routine matches created routine"):
		assert retrieved['id'] == routine_id
		assert retrieved['title'] == created['title']
		assert retrieved['description'] == created['description']
		assert retrieved['start_time'] == created['start_time']
		assert retrieved['end_time'] == created['end_time']
		assert retrieved['active'] == created['active']
		assert retrieved['created_at'] == created['created_at']


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_title(auth_client):
	"""Update routine title"""
	with allure.step("Create initial routine"):
		created = auth_client.post('/api/routines', {
			"title": "Original title"
		})
		routine_id = created['id']

	with allure.step("Update routine title"):
		updated = auth_client.put(f'/api/routines/{routine_id}', {
			"title": "Updated title"
		})

	with allure.step("Verify update"):
		assert updated['id'] == routine_id
		assert updated['title'] == "Updated title"
		assert updated['created_at'] == created['created_at']
		assert updated['updated_at'] >= created['updated_at']


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_description(auth_client):
	"""Update routine description"""
	with allure.step("Create routine with description"):
		created = auth_client.post('/api/routines', {
			"title": "Test routine",
			"description": "Original description"
		})
		routine_id = created['id']

	with allure.step("Update description"):
		updated = auth_client.put(f'/api/routines/{routine_id}', {
			"description": "New description"
		})

	with allure.step("Verify description updated"):
		assert updated['description'] == "New description"
		assert updated['title'] == created['title']


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_rrule(auth_client):
	"""Update routine recurrence rule"""
	with allure.step("Create routine"):
		created = auth_client.post('/api/routines', {
			"title": "Test routine",
			"rrule": "FREQ=WEEKLY;BYDAY=MO"
		})
		routine_id = created['id']

	with allure.step("Update rrule"):
		updated = auth_client.put(f'/api/routines/{routine_id}', {
			"rrule": "FREQ=DAILY"
		})

	with allure.step("Verify rrule updated"):
		assert updated['rrule'] == "FREQ=DAILY"
		assert updated['title'] == created['title']


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_start_time(auth_client):
	"""Update routine start time"""
	with allure.step("Create routine with time"):
		created = auth_client.post('/api/routines', {
			"title": "Test routine",
			"start_time": "06:00",
			"end_time": "07:00"
		})
		routine_id = created['id']

	with allure.step("Update start time"):
		updated = auth_client.put(f'/api/routines/{routine_id}', {
			"start_time": "07:00"
		})

	with allure.step("Verify start time updated"):
		assert updated['start_time'] == "07:00"
		assert updated['end_time'] == "07:00"  # End time unchanged


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_end_time(auth_client):
	"""Update routine end time"""
	with allure.step("Create routine with time"):
		created = auth_client.post('/api/routines', {
			"title": "Test routine",
			"start_time": "06:00",
			"end_time": "07:00"
		})
		routine_id = created['id']

	with allure.step("Update end time"):
		updated = auth_client.put(f'/api/routines/{routine_id}', {
			"end_time": "08:00"
		})

	with allure.step("Verify end time updated"):
		assert updated['end_time'] == "08:00"
		assert updated['start_time'] == "06:00"  # Start time unchanged


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_active_status(auth_client):
	"""Update routine active status"""
	with allure.step("Create active routine"):
		created = auth_client.post('/api/routines', {
			"title": "Test routine"
		})
		routine_id = created['id']
		assert created['active'] is True

	with allure.step("Mark routine as inactive"):
		updated = auth_client.put(f'/api/routines/{routine_id}', {
			"active": False
		})

	with allure.step("Verify active status changed"):
		assert updated['active'] is False
		assert updated['title'] == created['title']


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_back_to_active(auth_client):
	"""Update inactive routine back to active"""
	with allure.step("Create and deactivate routine"):
		created = auth_client.post('/api/routines', {
			"title": "Test routine"
		})
		routine_id = created['id']
		auth_client.put(f'/api/routines/{routine_id}', {
			"active": False
		})

	with allure.step("Reactivate routine"):
		reactivated = auth_client.put(f'/api/routines/{routine_id}', {
			"active": True
		})

	with allure.step("Verify routine is active again"):
		assert reactivated['active'] is True


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_multiple_routine_fields(auth_client):
	"""Update multiple routine fields at once"""
	with allure.step("Create initial routine"):
		created = auth_client.post('/api/routines', {
			"title": "Original",
			"description": "Original description",
			"rrule": "FREQ=WEEKLY;BYDAY=MO",
			"start_time": "06:00",
			"end_time": "07:00",
			"active": True
		})
		routine_id = created['id']

	with allure.step("Update multiple fields"):
		updated = auth_client.put(f'/api/routines/{routine_id}', {
			"title": "New title",
			"description": "New description",
			"rrule": "FREQ=DAILY",
			"start_time": "08:00",
			"end_time": "09:00",
			"active": False
		})

	with allure.step("Verify all updates applied"):
		assert updated['title'] == "New title"
		assert updated['description'] == "New description"
		assert updated['rrule'] == "FREQ=DAILY"
		assert updated['start_time'] == "08:00"
		assert updated['end_time'] == "09:00"
		assert updated['active'] is False


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_preserves_timestamps(auth_client):
	"""Verify created_at doesn't change on update"""
	with allure.step("Create routine"):
		created = auth_client.post('/api/routines', {"title": "Test"})
		original_created_at = created['created_at']

	with allure.step("Update routine"):
		updated = auth_client.put(f'/api/routines/{created["id"]}', {
			"title": "Updated"
		})

	with allure.step("Verify timestamps"):
		assert updated['created_at'] == original_created_at
		assert updated['updated_at'] >= original_created_at


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_empty_title_fails(auth_client):
	"""Update routine with empty title fails"""
	with allure.step("Create routine"):
		created = auth_client.post('/api/routines', {"title": "Test"})
		routine_id = created['id']

	with allure.step("Attempt to update with empty title"):
		response = auth_client.put(f'/api/routines/{routine_id}', {
			"title": ""
		}, handle_response=False)

	with allure.step("Verify error response"):
		assert response.status_code == 400


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_routine_returns_204(auth_client):
	"""Delete routine returns 204 No Content"""
	with allure.step("Create routine to delete"):
		created = auth_client.post('/api/routines', {"title": "Delete me"})
		routine_id = created['id']

	with allure.step("Delete routine"):
		response = auth_client.delete(f'/api/routines/{routine_id}',
									   handle_response=False)

	with allure.step("Verify 204 response"):
		assert response.status_code == 204


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_routine_removes_from_list(auth_client):
	"""Verify deleted routine no longer appears in list"""
	with allure.step("Create routine"):
		created = auth_client.post('/api/routines', {"title": "To delete"})
		routine_id = created['id']

	with allure.step("Verify routine in list"):
		routines_before = auth_client.get('/api/routines')
		routine_ids_before = [r['id'] for r in routines_before]
		assert routine_id in routine_ids_before

	with allure.step("Delete routine"):
		auth_client.delete(f'/api/routines/{routine_id}', handle_response=False)

	with allure.step("Verify routine removed from list"):
		routines_after = auth_client.get('/api/routines?active_only=false')
		routine_ids_after = [r['id'] for r in routines_after]
		assert routine_id not in routine_ids_after


@allure.feature('Routines')
@allure.story('Local Routine CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_routine_cannot_be_retrieved(auth_client):
	"""Verify deleted routine returns 404 on GET"""
	with allure.step("Create and delete routine"):
		created = auth_client.post('/api/routines', {"title": "Delete me"})
		routine_id = created['id']
		auth_client.delete(f'/api/routines/{routine_id}', handle_response=False)

	with allure.step("Attempt to retrieve deleted routine"):
		response = auth_client.get(f'/api/routines/{routine_id}',
								   handle_response=False)

	with allure.step("Verify 404 response"):
		assert response.status_code == 404