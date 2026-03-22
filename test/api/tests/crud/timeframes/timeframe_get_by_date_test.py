import pytest
import allure


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Date')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_date_creates_if_missing(auth_client):
    """Get timeframe for date creates if missing (get-or-create)"""
    with allure.step("Request day timeframe for specific date"):
        response = auth_client.get('/api/timeframes/day/2025-06-08')

    with allure.step("Verify timeframe created"):
        assert response['id']
        assert response['kind'] == 'day'

    with allure.step("Verify timeframe is for today"):
        assert "2025-06-08" in response['start_at']
        assert "2025-06-09" in response['end_at']


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Date')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_date_returns_existing(auth_client):
    """Get timeframe for date returns existing (idempotent)"""
    with allure.step("Request timeframe first time"):
        first = auth_client.get('/api/timeframes/week/2025-06-08')
        first_id = first['id']

    with allure.step("Request same timeframe again"):
        second = auth_client.get('/api/timeframes/week/2025-06-08')
        second_id = second['id']

    with allure.step("Verify same timeframe returned"):
        assert first_id == second_id
        assert first['start_at'] == second['start_at']
        assert first['end_at'] == second['end_at']
        assert first['label'] == second['label']
        assert first['created_at'] == second['created_at']


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Date')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_date_with_invalid_kind(auth_client):
    """Get timeframe for date with invalid kind returns 400"""
    with allure.step("Request timeframe with invalid kind"):
        response = auth_client.get('/api/timeframes/invalid_kind/2025-06-08',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Date')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_date_with_invalid_date_format(auth_client):
    """Get timeframe for date with invalid date format returns 400"""
    with allure.step("Request timeframe with invalid date"):
        response = auth_client.get('/api/timeframes/day/not-a-date',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()

    with allure.step("Verify error message"):
        assert 'error' in error_data
        assert 'invalid date format' in error_data['error'].lower()


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Date')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_date_with_tz_parameter(auth_client):
    """Get timeframe for date with tz parameter"""
    with allure.step("Request timeframe with timezone"):
        response = auth_client.get('/api/timeframes/month/2025-06-15?tz=Europe/London')

    with allure.step("Verify month timeframe created"):
        assert response['kind'] == 'month'

    with allure.step("Verify timeframe is of the correct month"):
        assert "2025-06-01" in response['start_at']
        assert "2025-07-01" in response['end_at']


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Date')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_date_with_invalid_timezone(auth_client):
    """Get timeframe for date with invalid timezone returns 400"""
    with allure.step("Request timeframe with invalid timezone"):
        response = auth_client.get('/api/timeframes/day/2025-06-08?tz=BadZone/Invalid',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()

    with allure.step("Verify error message"):
        assert 'error' in error_data
        assert 'invalid timezone' in error_data['error'].lower()


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Date')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_date_for_each_kind(auth_client):
    """Get timeframe for date for each supported kind"""
    kinds = ['day', 'week', 'month', 'season', 'year']

    for kind in kinds:
        with allure.step(f"Request {kind} timeframe for specific date"):
            response = auth_client.get(f'/api/timeframes/{kind}/2025-06-08')

        with allure.step(f"Verify {kind} timeframe returned"):
            assert response['id']
            assert response['kind'] == kind
            assert response['start_at']
            assert response['end_at']
            assert response['label']