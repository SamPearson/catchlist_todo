import pytest
import allure
from datetime import datetime, timedelta


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_sessions_for_weekly_routine(auth_client):
	"""Generate sessions for a routine with weekly recurrence"""
	with allure.step("Create routine with weekly Monday recurrence"):
		routine = auth_client.post('/api/routines', {
			"title": "Weekly Monday Meeting",
			"rrule": "FREQ=WEEKLY;BYDAY=MO",
			"start_time": "10:00",
			"end_time": "11:00"
		})
		routine_id = routine['id']

	with allure.step("Generate sessions for January 2025"):
		response = auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-31"
			}
		)

	with allure.step("Verify sessions were created"):
		assert isinstance(response, list)
		assert len(response) > 0

		# January 2025 Mondays: 6, 13, 20, 27
		# Should return only newly created sessions
		assert len(response) == 4

	with allure.step("Verify session structure and times"):
		for session in response:
			assert 'id' in session
			assert session['routine_id'] == routine_id
			assert session['start_time'] is not None
			assert session['end_time'] is not None
			assert session['completed'] is False
			# Sessions should be 1 hour long (10:00 to 11:00)
			start = datetime.fromisoformat(session['start_time'])
			end = datetime.fromisoformat(session['end_time'])
			delta = end - start
			assert delta.total_seconds() == 3600  # 1 hour


	@allure.feature('Routines')
	@allure.story('Session Generation')
	@pytest.mark.routines
	@pytest.mark.sessions
	@pytest.mark.smoke_test
	@allure.severity(allure.severity_level.CRITICAL)
	def test_generate_sessions_for_daily_routine(auth_client):
		"""Generate sessions for a routine with daily recurrence"""
		with allure.step("Create routine with daily recurrence"):
			routine = auth_client.post('/api/routines', {
				"title": "Daily Standup",
				"rrule": "FREQ=DAILY",
				"start_time": "09:00",
				"end_time": "09:30"
			})
			routine_id = routine['id']

		with allure.step("Generate sessions for 7 days"):
			response = auth_client.post(
				f'/api/routines/{routine_id}/sessions/generate',
				{
					"start_date": "2025-01-01",
					"end_date": "2025-01-07"
				}
			)

		with allure.step("Verify sessions were created"):
			assert isinstance(response, list)
			assert len(response) == 7  # 7 days

		with allure.step("Verify session structure"):
			for i, session in enumerate(response):
				assert session['routine_id'] == routine_id
				assert session['completed'] is False
				# Each session is 30 minutes
				start = datetime.fromisoformat(session['start_time'])
				end = datetime.fromisoformat(session['end_time'])
				delta = end - start
				assert delta.total_seconds() == 1800  # 30 minutes


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_sessions_respects_time_boundaries(auth_client):
	"""Verify generated sessions use routine's start and end times"""
	with allure.step("Create routine with specific times"):
		routine = auth_client.post('/api/routines', {
			"title": "Morning Yoga",
			"rrule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
			"start_time": "06:30",
			"end_time": "07:30"
		})
		routine_id = routine['id']

	with allure.step("Generate sessions"):
		response = auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-31"
			}
		)

	with allure.step("Verify all sessions have correct times"):
		for session in response:
			start = datetime.fromisoformat(session['start_time'])
			end = datetime.fromisoformat(session['end_time'])

			# Check time of day is correct
			assert start.hour == 6
			assert start.minute == 30
			assert end.hour == 7
			assert end.minute == 30


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_sessions_no_rrule_fails(auth_client):
	"""Generate sessions for routine without rrule fails"""
	with allure.step("Create routine without rrule"):
		routine = auth_client.post('/api/routines', {
			"title": "No Recurrence",
			"start_time": "10:00",
			"end_time": "11:00"
		})
		routine_id = routine['id']

	with allure.step("Attempt to generate sessions"):
		response = auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-31"
			},
			handle_response=False
		)

	with allure.step("Verify error response"):
		assert response.status_code == 400
		error = response.json()
		assert 'error' in error


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_sessions_no_start_time_fails(auth_client):
	"""Generate sessions for routine without start_time fails"""
	with allure.step("Create routine without start_time"):
		routine = auth_client.post('/api/routines', {
			"title": "No Start Time",
			"rrule": "FREQ=DAILY"
		})
		routine_id = routine['id']

	with allure.step("Attempt to generate sessions"):
		response = auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-31"
			},
			handle_response=False
		)

	with allure.step("Verify error response"):
		assert response.status_code == 400
		error = response.json()
		assert 'error' in error

# dont actually want to generate routines with no start date
# but save this for when we do negative testing.
# @allure.feature('Routines')
# @allure.story('Session Generation')
# @pytest.mark.routines
# @pytest.mark.sessions
# @allure.severity(allure.severity_level.CRITICAL)
# def test_generate_sessions_missing_start_date(auth_client):
# 	"""Generate sessions without start_date fails"""
# 	with allure.step("Create routine"):
# 		routine = auth_client.post('/api/routines', {
# 			"title": "Test Routine",
# 			"rrule": "FREQ=DAILY",
# 			"start_time": "10:00"
# 		})
# 		routine_id = routine['id']
#
# 	with allure.step("Attempt to generate without start_date"):
# 		response = auth_client.post(
# 			f'/api/routines/{routine_id}/sessions/generate',
# 			{
# 				"end_date": "2025-01-31"
# 			},
# 			handle_response=False
# 		)
#
# 	with allure.step("Verify error response"):
# 		assert response.status_code == 400
# 		error = response.json()
# 		assert 'error' in error
#
#
# dont actually want to generate routines with no end date
# but save this for when we do negative testing.
# @allure.feature('Routines')
# @allure.story('Session Generation')
# @pytest.mark.routines
# @pytest.mark.sessions
# @allure.severity(allure.severity_level.CRITICAL)
# def test_generate_sessions_missing_end_date(auth_client):
# 	"""Generate sessions without end_date fails"""
# 	with allure.step("Create routine"):
# 		routine = auth_client.post('/api/routines', {
# 			"title": "Test Routine",
# 			"rrule": "FREQ=DAILY",
# 			"start_time": "10:00"
# 		})
# 		routine_id = routine['id']
#
# 	with allure.step("Attempt to generate without end_date"):
# 		response = auth_client.post(
# 			f'/api/routines/{routine_id}/sessions/generate',
# 			{
# 				"start_date": "2025-01-01"
# 			},
# 			handle_response=False
# 		)
#
# 	with allure.step("Verify error response"):
# 		assert response.status_code == 400


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_sessions_nonexistent_routine_fails(auth_client):
	"""Generate sessions for nonexistent routine fails"""
	with allure.step("Attempt to generate for invalid routine ID"):
		response = auth_client.post(
			'/api/routines/999999/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-31"
			},
			handle_response=False
		)

	with allure.step("Verify error response"):
		assert response.status_code == 400


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_same_range_twice_no_duplicates(isolated_auth_client):
	"""Re-generating sessions for same date range doesn't create duplicates"""
	with allure.step("Create routine"):
		routine = isolated_auth_client.post('/api/routines', {
			"title": "Daily Routine",
			"rrule": "FREQ=DAILY",
			"start_time": "09:00",
			"end_time": "10:00"
		})
		routine_id = routine['id']

	with allure.step("Generate sessions for January 1-7"):
		first_response = isolated_auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-07"
			}
		)
		first_count = len(first_response)

	with allure.step("Generate sessions again for same range"):
		second_response = isolated_auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-07"
			}
		)
		second_count = len(second_response)

	with allure.step("Verify no duplicates created"):
		# Second generation should return 0 sessions (all already exist)
		assert second_count == 0
		assert first_count == 7


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_overlapping_range_only_new_dates(isolated_auth_client):
	"""Re-generating with overlapping date range only creates new sessions"""
	with allure.step("Create routine"):
		routine = isolated_auth_client.post('/api/routines', {
			"title": "Daily Routine",
			"rrule": "FREQ=DAILY",
			"start_time": "09:00",
			"end_time": "10:00"
		})
		routine_id = routine['id']

	with allure.step("Generate sessions for January 1-10"):
		first_response = isolated_auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-10"
			}
		)
		first_count = len(first_response)

	with allure.step("Generate sessions for January 5-15 (overlapping)"):
		second_response = isolated_auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-05",
				"end_date": "2025-01-15"
			}
		)
		second_count = len(second_response)

	with allure.step("Verify only new dates were created"):
		# Jan 1-10 = 10 days
		# Jan 5-15 overlaps Jan 5-10 (already exist) but adds Jan 11-15 (5 new)
		assert first_count == 10, f"Expected 10 sessions from first generation, got {first_count}"
		assert second_count == 5, f"Expected 5 new sessions from overlapping generation, got {second_count}"


@allure.feature('Routines')
@allure.story('Session Generation')
@pytest.mark.routines
@pytest.mark.sessions
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_sessions_multiple_weekly_days(isolated_auth_client):
	"""Generate sessions for routine recurring on multiple days per week"""
	with allure.step("Create routine with Mon/Wed/Fri recurrence"):
		routine = isolated_auth_client.post('/api/routines', {
			"title": "Gym Days",
			"rrule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
			"start_time": "18:00",
			"end_time": "19:30"
		})
		routine_id = routine['id']

	with allure.step("Generate sessions for January 2025"):
		response = isolated_auth_client.post(
			f'/api/routines/{routine_id}/sessions/generate',
			{
				"start_date": "2025-01-01",
				"end_date": "2025-01-31"
			}
		)

	with allure.step("Verify sessions for each occurrence"):
		# January 2025: Mon(6,13,20,27), Wed(1,8,15,22,29), Fri(3,10,17,24,31)
		# Total = 14 sessions (4 Mondays + 5 Wednesdays + 5 Fridays)
		assert len(response) == 14

	with allure.step("Verify each session has correct duration"):
		for session in response:
			start = datetime.fromisoformat(session['start_time'])
			end = datetime.fromisoformat(session['end_time'])
			# 1.5 hours = 5400 seconds
			delta = end - start
			assert delta.total_seconds() == 5400


# @allure.feature('Routines')
# @allure.story('Session Generation')
# @pytest.mark.routines
# @pytest.mark.sessions
# @allure.severity(allure.severity_level.CRITICAL)
# def test_generate_sessions_empty_end_time(auth_client):
# 	"""Generate sessions for routine without end_time"""
# 	with allure.step("Create routine without end_time"):
# 		routine = auth_client.post('/api/routines', {
# 			"title": "No End Time",
# 			"rrule": "FREQ=DAILY",
# 			"start_time": "10:00"
# 		})
# 		routine_id = routine['id']
#
# 	with allure.step("Generate sessions"):
# 		response = auth_client.post(
# 			f'/api/routines/{routine_id}/sessions/generate',
# 			{
# 				"start_date": "2025-01-01",
# 				"end_date": "2025-01-07"
# 			}
# 		)
#
# 	with allure.step("Verify sessions were created"):
# 		assert len(response) == 7
#
# 	with allure.step("Verify sessions have matching start/end times"):
# 		for session in response:
# 			start = datetime.fromisoformat(session['start_time'])
# 			end = datetime.fromisoformat(session['end_time'])
# 			# Start time should be 10:00, end time should also be a valid time
# 			assert start.hour == 10
# 			assert start.minute == 0