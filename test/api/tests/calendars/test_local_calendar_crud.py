
import pytest
import allure


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_local_calendar_with_required_fields(auth_client):
	"""Create local calendar with only required field (name)"""
	with allure.step("Prepare test data"):
		data = {"name": "Test Local Calendar"}

	with allure.step("Create new local calendar"):
		response = auth_client.post('/api/calendars', data)

	with allure.step("Verify response structure and values"):
		# Response contains ID and timestamps
		assert response['id']
		assert isinstance(response['id'], int)

		# Name matches input
		assert response['name'] == data['name']
		assert isinstance(response['name'], str)

		# Color defaults to #767676
		assert response['color'] == '#767676'
		assert isinstance(response['color'], str)

		# Timestamps present
		assert response['created_at']
		assert response['updated_at']
		assert isinstance(response['created_at'], str)
		assert isinstance(response['updated_at'], str)

		# External fields should be null for local calendars
		assert response['external_uid'] is None
		assert response['external_source'] is None


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_local_calendar_with_custom_color(auth_client):
	"""Create local calendar with custom color"""
	with allure.step("Prepare test data"):
		data = {
			"name": "Colorful Calendar",
			"color": "#FF5733"
		}

	with allure.step("Create new local calendar"):
		response = auth_client.post('/api/calendars', data)

	with allure.step("Verify color is stored"):
		assert response['color'] == data['color']
		assert isinstance(response['color'], str)
		assert response['name'] == data['name']


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_multiple_local_calendars(auth_client):
	"""Create multiple local calendars to verify independence"""
	with allure.step("Create first calendar"):
		calendar1 = auth_client.post('/api/calendars', {"name": "Calendar 1"})
		calendar1_id = calendar1['id']

	with allure.step("Create second calendar"):
		calendar2 = auth_client.post('/api/calendars', {"name": "Calendar 2"})
		calendar2_id = calendar2['id']

	with allure.step("Verify calendars are independent"):
		assert calendar1_id != calendar2_id
		assert calendar1['name'] != calendar2['name']
		# Timestamps should be close but not identical
		assert calendar1['created_at'] <= calendar2['created_at']

@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_calendars_returns_list(auth_client):
	"""Retrieve all calendars for authenticated user"""
	with allure.step("Create multiple test calendars"):
		created_ids = []
		for i in range(3):
			calendar = auth_client.post('/api/calendars', {
				"name": f"Test calendar {i+1}"
			})
			created_ids.append(calendar['id'])

	with allure.step("Retrieve all calendars"):
		response = auth_client.get('/api/calendars')

	with allure.step("Verify response structure"):
		assert isinstance(response, list)
		assert len(response) >= 3

		# Verify each calendar has required fields
		for calendar in response:
			assert calendar['id']
			assert calendar['name']
			assert 'color' in calendar
			assert 'created_at' in calendar
			assert 'updated_at' in calendar
			assert 'active' in calendar

	with allure.step("Verify created calendars are in list"):
		retrieved_ids = [c['id'] for c in response]
		for created_id in created_ids:
			assert created_id in retrieved_ids


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_calendar_name(auth_client):
	"""Update calendar name"""
	with allure.step("Create initial calendar"):
		created = auth_client.post('/api/calendars', {
			"name": "Original name"
		})
		calendar_id = created['id']

	with allure.step("Update calendar name"):
		updated = auth_client.put(f'/api/calendars/{calendar_id}', {
			"name": "Updated name"
		})

	with allure.step("Verify update"):
		assert updated['id'] == calendar_id
		assert updated['name'] == "Updated name"
		assert updated['created_at'] == created['created_at']
		assert updated['updated_at'] >= created['updated_at']


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_calendar_color(auth_client):
	"""Update calendar color"""
	with allure.step("Create calendar with default color"):
		created = auth_client.post('/api/calendars', {
			"name": "Test calendar",
			"color": "#AAAAAA"
		})
		calendar_id = created['id']

	with allure.step("Update calendar color"):
		updated = auth_client.put(f'/api/calendars/{calendar_id}', {
			"color": "#BBBBBB"
		})

	with allure.step("Verify color updated"):
		assert updated['color'] == "#BBBBBB"
		assert updated['name'] == created['name']  # Name unchanged


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_calendar_active_status(auth_client):
	"""Update calendar active status"""
	with allure.step("Create active calendar"):
		created = auth_client.post('/api/calendars', {
			"name": "Test calendar"
		})
		calendar_id = created['id']
		assert created['active'] is True

	with allure.step("Mark calendar as inactive"):
		updated = auth_client.put(f'/api/calendars/{calendar_id}', {
			"active": False
		})

	with allure.step("Verify active status changed"):
		assert updated['active'] is False
		assert updated['name'] == created['name']


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_calendar_back_to_active(auth_client):
	"""Update inactive calendar back to active"""
	with allure.step("Create and deactivate calendar"):
		created = auth_client.post('/api/calendars', {
			"name": "Test calendar"
		})
		calendar_id = created['id']
		auth_client.put(f'/api/calendars/{calendar_id}', {
			"active": False
		})

	with allure.step("Reactivate calendar"):
		reactivated = auth_client.put(f'/api/calendars/{calendar_id}', {
			"active": True
		})

	with allure.step("Verify calendar is active again"):
		assert reactivated['active'] is True


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_multiple_calendar_fields(auth_client):
	"""Update multiple calendar fields at once"""
	with allure.step("Create initial calendar"):
		created = auth_client.post('/api/calendars', {
			"name": "Original",
			"color": "#AAAAAA",
			"active": True
		})
		calendar_id = created['id']

	with allure.step("Update multiple fields"):
		updated = auth_client.put(f'/api/calendars/{calendar_id}', {
			"name": "New name",
			"color": "#BBBBBB",
			"active": False
		})

	with allure.step("Verify all updates applied"):
		assert updated['name'] == "New name"
		assert updated['color'] == "#BBBBBB"
		assert updated['active'] is False


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_preserves_timestamps(auth_client):
	"""Verify created_at doesn't change on update"""
	with allure.step("Create calendar"):
		created = auth_client.post('/api/calendars', {"name": "Test"})
		original_created_at = created['created_at']

	with allure.step("Update calendar"):
		updated = auth_client.put(f'/api/calendars/{created["id"]}', {
			"name": "Updated"
		})

	with allure.step("Verify timestamps"):
		assert updated['created_at'] == original_created_at
		assert updated['updated_at'] >= original_created_at


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_calendars_exclude_inactive_by_default(auth_client):
	"""List calendars filters out inactive calendars by default"""
	with allure.step("Create active calendar"):
		active_calendar = auth_client.post('/api/calendars', {
			"name": "Active calendar"
		})
		active_id = active_calendar['id']

	with allure.step("Create and deactivate a calendar"):
		inactive_calendar = auth_client.post('/api/calendars', {
			"name": "Inactive calendar"
		})
		inactive_id = inactive_calendar['id']
		auth_client.put(f'/api/calendars/{inactive_id}', {
			"active": False
		})

	with allure.step("Retrieve all calendars without filter"):
		response = auth_client.get('/api/calendars')

	with allure.step("Verify inactive calendar is excluded"):
		retrieved_ids = [c['id'] for c in response]
		assert active_id in retrieved_ids
		assert inactive_id not in retrieved_ids


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_calendar_returns_204(auth_client):
	"""Delete calendar returns 204 No Content"""
	with allure.step("Create calendar to delete"):
		created = auth_client.post('/api/calendars', {"name": "Delete me"})
		calendar_id = created['id']

	with allure.step("Delete calendar"):
		response = auth_client.delete(f'/api/calendars/{calendar_id}',
									   handle_response=False)

	with allure.step("Verify 204 response"):
		assert response.status_code == 204


@allure.feature('Calendars')
@allure.story('Local Calendar CRUD Operations')
@pytest.mark.calendars
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_calendar_removes_from_list(auth_client):
	"""Verify deleted calendar no longer appears in list"""
	with allure.step("Create calendar"):
		created = auth_client.post('/api/calendars', {"name": "To delete"})
		calendar_id = created['id']

	with allure.step("Verify calendar in list"):
		calendars_before = auth_client.get('/api/calendars')
		calendar_ids_before = [c['id'] for c in calendars_before]
		assert calendar_id in calendar_ids_before

	with allure.step("Delete calendar"):
		auth_client.delete(f'/api/calendars/{calendar_id}', handle_response=False)

	with allure.step("Verify calendar removed from list"):
		calendars_after = auth_client.get('/api/calendars')
		calendar_ids_after = [c['id'] for c in calendars_after]
		assert calendar_id not in calendar_ids_after