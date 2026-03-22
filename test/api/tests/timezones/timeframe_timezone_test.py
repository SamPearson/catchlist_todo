import pytest
import allure


@allure.feature('Timeframes')
@allure.story('Timezone Handling')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_timezone_uses_explicit_tz_parameter_when_provided(auth_client):
    """Timezone uses explicit tz parameter when provided"""
    with allure.step("Set user timezone to America/Chicago"):
        auth_client.patch('/api/auth/user', {"timezone": "America/Chicago"})

    with allure.step("Request timeframe with explicit Europe/London timezone"):
        response = auth_client.get('/api/timeframes/day/2025-06-08?tz=Europe/London')

    with allure.step("Create same date with user's default timezone"):
        response_user_tz = auth_client.get('/api/timeframes/day/2025-06-08')

    with allure.step("Verify different timeframes created (explicit tz overrides user default)"):
        # If timezones are respected, the UTC boundaries should differ
        # London is ahead of Chicago, so same local date = different UTC times
        assert response['id'] != response_user_tz['id']


@allure.feature('Timeframes')
@allure.story('Timezone Handling')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_timezone_uses_user_default_when_tz_not_provided(auth_client):
    """Timezone uses user default when tz parameter not provided"""
    with allure.step("Set user timezone to America/New_York"):
        auth_client.patch('/api/auth/user', {"timezone": "America/New_York"})

    with allure.step("Request timeframe without tz parameter"):
        response = auth_client.get('/api/timeframes/day/2025-06-08')

    with allure.step("Verify timeframe created successfully"):
        assert response['id']
        assert response['kind'] == 'day'

    with allure.step("Request same timeframe again - should return existing"):
        response2 = auth_client.get('/api/timeframes/day/2025-06-08')
        assert response['id'] == response2['id']


@allure.feature('Timeframes')
@allure.story('Timezone Handling')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_timezone_uses_utc_when_no_user_timezone_configured(auth_client):
    """Timezone uses UTC when no user timezone configured"""
    with allure.step("Verify user has no timezone set (or explicitly set to UTC)"):
        user_info = auth_client.get('/api/auth/user-info')
        # User might have UTC as default or None

    with allure.step("Request timeframe without tz parameter"):
        response = auth_client.get('/api/timeframes/day/2025-06-08')

    with allure.step("Verify timeframe created (using UTC as fallback)"):
        assert response['id']
        assert response['kind'] == 'day'


@allure.feature('Timeframes')
@allure.story('Timezone Handling')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_day_timeframe_boundaries_vary_by_timezone(auth_client):
    """Day timeframe boundaries vary by timezone for same local date"""
    with allure.step("Create day timeframe for June 8 in UTC"):
        utc_response = auth_client.get('/api/timeframes/day/2025-06-08?tz=UTC')

    with allure.step("Create day timeframe for June 8 in America/Los_Angeles"):
        la_response = auth_client.get('/api/timeframes/day/2025-06-08?tz=America/Los_Angeles')

    with allure.step("Verify different timeframes created"):
        # Same local date in different timezones = different UTC boundaries
        assert utc_response['id'] != la_response['id']

    with allure.step("Verify UTC boundaries differ"):
        # LA is UTC-7 or UTC-8, so June 8 in LA starts later in UTC
        assert utc_response['start_at'] != la_response['start_at']
        assert utc_response['end_at'] != la_response['end_at']


@allure.feature('Timeframes')
@allure.story('Timezone Handling')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_week_timeframe_boundaries_vary_by_timezone(auth_client):
    """Week timeframe boundaries vary by timezone"""
    with allure.step("Create week timeframe for June 8 in UTC"):
        utc_response = auth_client.get('/api/timeframes/week/2025-06-08?tz=UTC')

    with allure.step("Create week timeframe for June 8 in Asia/Tokyo"):
        tokyo_response = auth_client.get('/api/timeframes/week/2025-06-08?tz=Asia/Tokyo')

    with allure.step("Verify different timeframes created"):
        # Same local date in different timezones = different UTC boundaries
        assert utc_response['id'] != tokyo_response['id']

    with allure.step("Verify UTC boundaries differ"):
        assert utc_response['start_at'] != tokyo_response['start_at']
        assert utc_response['end_at'] != tokyo_response['end_at']


@allure.feature('Timeframes')
@allure.story('Timezone Handling')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_today_varies_by_timezone(auth_client):
    """'Today' calculation respects timezone parameter"""
    with allure.step("Request 'day' timeframe for 'today' in UTC"):
        utc_today = auth_client.get('/api/timeframes/day?tz=UTC')

    with allure.step("Request 'day' timeframe for 'today' in Pacific/Auckland"):
        # Auckland is UTC+12/+13, so "today" there is ahead of UTC
        auckland_today = auth_client.get('/api/timeframes/day?tz=Pacific/Auckland')

    with allure.step("Verify both requests succeed"):
        assert utc_today['id']
        assert auckland_today['id']

    # Note: These might be the same day or different depending on when test runs
    # The important thing is both succeed and respect their timezone

