import pytest
import allure


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Today')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_today_creates_if_missing(auth_client):
    """Get timeframe for today creates if missing (get-or-create)"""
    with allure.step("Request day timeframe for today"):
        response = auth_client.get('/api/timeframes/day')

    with allure.step("Verify timeframe created"):
        assert response['id']
        assert response['kind'] == 'day'
        assert response['start_at']
        assert response['end_at']
        assert response['label']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Today')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_today_returns_existing(auth_client):
    """Get timeframe for today returns existing (idempotent)"""
    with allure.step("Request timeframe first time"):
        first = auth_client.get('/api/timeframes/week')
        first_id = first['id']

    with allure.step("Request same timeframe again"):
        second = auth_client.get('/api/timeframes/week')
        second_id = second['id']

    with allure.step("Verify same timeframe returned"):
        assert first_id == second_id
        assert first['start_at'] == second['start_at']
        assert first['end_at'] == second['end_at']
        assert first['label'] == second['label']
        assert first['created_at'] == second['created_at']


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Today')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_today_with_invalid_kind(auth_client):
    """Get timeframe for today with invalid kind returns 400"""
    with allure.step("Request timeframe with invalid kind"):
        response = auth_client.get('/api/timeframes/invalid_kind',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Today')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_today_with_tz_parameter(auth_client):
    """Get timeframe for today with tz parameter"""
    with allure.step("Request timeframe with timezone"):
        response = auth_client.get('/api/timeframes/month?tz=America/New_York')

    with allure.step("Verify timeframe created"):
        assert response['id']
        assert response['kind'] == 'month'
        assert response['start_at']
        assert response['end_at']
        assert response['label']


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Today')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_today_with_invalid_timezone(auth_client):
    """Get timeframe for today with invalid timezone returns 400"""
    with allure.step("Request timeframe with invalid timezone"):
        response = auth_client.get('/api/timeframes/day?tz=Not/Valid',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data
        assert 'invalid timezone' in error_data['error'].lower()


@allure.feature('Timeframes')
@allure.story('Get Timeframe for Today')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_for_today_for_each_kind(auth_client):
    """Get timeframe for today for each supported kind"""
    kinds = ['day', 'week', 'month', 'season', 'year']

    for kind in kinds:
        with allure.step(f"Request {kind} timeframe for today"):
            response = auth_client.get(f'/api/timeframes/{kind}')

        with allure.step(f"Verify {kind} timeframe returned"):
            assert response['id']
            assert response['kind'] == kind
            assert response['start_at']
            assert response['end_at']
            assert response['label']