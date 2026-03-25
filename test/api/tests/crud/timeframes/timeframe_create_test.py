import pytest
import allure
from datetime import datetime, date
from zoneinfo import ZoneInfo

@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_with_kind_only(auth_client):
    """Create timeframe with kind only defaults to today in UTC"""
    with allure.step("Create timeframe with only kind"):
        response = auth_client.post('/api/timeframes', {"kind": "day"})

    with allure.step("Verify timeframe created successfully"):
        assert response['kind'] == 'day'

    with allure.step("Verify timeframe is for today"):
        # Parse the ISO format datetime and extract the date
        start_dt = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

        today = datetime.now(ZoneInfo("UTC")).date() # explicitly use UTC timezone
        assert start_dt.date() == today
        assert (end_dt - start_dt).days == 1  # One day duration


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_with_kind_date_and_tz(auth_client):
    """Create timeframe with kind, date, and timezone"""
    with allure.step("Create timeframe with specific timezone"):
        response = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08",
            "tz": "America/Chicago"
        })

    with allure.step("Verify timeframe created"):
        assert response['kind'] == 'day'

    with allure.step("Verify timeframe is for today"):
        assert "2025-06-08" in response['start_at']
        assert "2025-06-09" in response['end_at']


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_without_kind(auth_client):
    """Create timeframe without kind returns 400"""
    with allure.step("Attempt to create timeframe without kind"):
        response = auth_client.post('/api/timeframes', {
            "date": "2025-06-08"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400



@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_with_invalid_kind(auth_client):
    """Create timeframe with invalid kind returns 400"""
    with allure.step("Attempt to create timeframe with invalid kind"):
        response = auth_client.post('/api/timeframes', {
            "kind": "invalid_kind"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_with_invalid_date_format(auth_client):
    """Create timeframe with invalid date format returns 400"""
    with allure.step("Attempt to create timeframe with invalid date"):
        response = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "not-a-date"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400

    with allure.step("Verify correct error message"):
        assert response['error']
        assert 'invalid date format' in response['error'].lower()


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_with_invalid_timezone(auth_client):
    """Create timeframe with invalid timezone returns 400"""
    with allure.step("Attempt to create timeframe with invalid timezone"):
        response = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08",
            "tz": "Invalid/Timezone"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400

    with allure.step("Verify correct error message"):
        assert response['error']
        assert 'invalid timezone' in response['error'].lower()


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_with_empty_request_body(auth_client):
    """Create timeframe with empty request body returns 400"""
    with allure.step("Attempt to create timeframe with empty body"):
        response = auth_client.post('/api/timeframes', {}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_returns_201_always(auth_client):
    """Create timeframe returns 201 even if already exists"""
    with allure.step("Create initial timeframe"):
        response1 = auth_client.post('/api/timeframes', {
            "kind": "month",
            "date": "2025-06-15"
        }, handle_response=False)

    with allure.step("Verify 201 status code"):
        assert response1.status_code == 201

    with allure.step("Create duplicate timeframe"):
        response2 = auth_client.post('/api/timeframes', {
            "kind": "month",
            "date": "2025-06-15"
        }, handle_response=False)

    with allure.step("Verify 201 status code again"):
        assert response2.status_code == 201


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_duplicate_timeframe_returns_existing(auth_client):
    """Create duplicate timeframe returns existing timeframe (get-or-create)"""
    with allure.step("Create initial timeframe"):
        first = auth_client.post('/api/timeframes', {
            "kind": "season",
            "date": "2025-07-15"  # Summer 2025
        })
        first_id = first['id']

    with allure.step("Create duplicate timeframe with same kind and period"):
        second = auth_client.post('/api/timeframes', {
            "kind": "season",
            "date": "2025-08-01"  # Also Summer 2025
        })
        second_id = second['id']

    with allure.step("Verify same timeframe returned"):
        assert first_id == second_id
        assert first['start_at'] == second['start_at']
        assert first['end_at'] == second['end_at']
        assert first['label'] == second['label']


@allure.feature('Timeframes')
@allure.story('Create Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.create
@allure.severity(allure.severity_level.NORMAL)
def test_create_timeframe_for_each_kind(auth_client):
    """Create timeframe for each supported kind"""
    kinds = ['day', 'week', 'month', 'season', 'year']

    for kind in kinds:
        with allure.step(f"Create {kind} timeframe"):
            response = auth_client.post('/api/timeframes', {
                "kind": kind,
                "date": "2025-06-08"
            })

        with allure.step(f"Verify {kind} timeframe created"):
            assert response['kind'] == kind
