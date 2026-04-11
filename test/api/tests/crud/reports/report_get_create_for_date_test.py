import pytest
import allure
from datetime import date, datetime, timedelta
from utils.data_factories.entity_factory import create_task


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_for_day(auth_client):
    """Get or create report with kind=day works"""

    with allure.step("Get or create daily report"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/day/{today}')

    with allure.step("Verify report returned"):
        assert response.status_code == 200
        assert 'report_type' in response
        assert response['report_type'] == 'day'
        assert 'plan' in response
        assert 'reason' in response
        assert 'pre_notes' in response
        assert 'post_notes' in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_for_week(auth_client):
    """Get or create report with kind=week works"""

    with allure.step("Get or create weekly report"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/week/{today}')

    with allure.step("Verify report returned"):
        assert response.status_code == 200
        assert 'report_type' in response
        assert response['report_type'] == 'week'
        assert 'plan' in response
        assert 'reason' in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_for_month(auth_client):
    """Get or create report with kind=month works"""

    with allure.step("Get or create monthly report"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/month/{today}')

    with allure.step("Verify report returned"):
        assert response.status_code == 200
        assert 'report_type' in response
        assert response['report_type'] == 'month'
        assert 'plan' in response
        assert 'reason' in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_for_season(auth_client):
    """Get or create report with kind=season works"""

    with allure.step("Get or create seasonal report"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/season/{today}')

    with allure.step("Verify report returned"):
        assert response.status_code == 200
        assert 'report_type' in response
        assert response['report_type'] == 'season'
        assert 'plan' in response
        assert 'reason' in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_for_year(auth_client):
    """Get or create report with kind=year works"""

    with allure.step("Get or create yearly report"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/year/{today}')

    with allure.step("Verify report returned"):
        assert response.status_code == 200
        assert 'report_type' in response
        assert response['report_type'] == 'year'
        assert 'plan' in response
        assert 'reason' in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_creates_timeframe_if_missing(auth_client):
    """Get or create report auto-creates associated timeframe"""

    with allure.step("Get or create report for new date"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/day/{today}', params={'full': True})

    with allure.step("Verify timeframe was created"):
        assert response.status_code == 200
        assert 'timeframe_id' in response
        assert response['timeframe_id'] is not None

        # Verify timeframe exists
        timeframe_id = response['timeframe_id']
        timeframe_response = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe_response.status_code == 200


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_returns_existing_report(auth_client):
    """Call get-or-create twice with same kind/date, verify same report ID"""

    with allure.step("Get or create report first time"):
        today = date.today().isoformat()
        first_response = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        first_id = first_response['id']

    with allure.step("Get or create report second time"):
        second_response = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        second_id = second_response['id']

    with allure.step("Verify same report ID returned"):
        assert first_id == second_id


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_commitment_scope_window(auth_client):
    """Get or create report with commitment_scope=window (default) includes commitments"""

    with allure.step("Create task and commitment"):
        today = date.today().isoformat()
        task = create_task(auth_client, title="Task for window scope")

        # Create commitment to this day
        auth_client.post('/api/commitments/soft', data={
            'target_type': 'task',
            'target_id': task['id'],
            'timeframe_kind': 'day',
            'reference_date': today
        })

    with allure.step("Get or create report with default commitment_scope"):
        response = auth_client.get(f'/api/reports/day/{today}')

    with allure.step("Verify commitments included"):
        assert response.status_code == 200
        assert 'commitments' in response
        assert 'stats' in response
        assert isinstance(response['commitments'], list)
        assert len(response['commitments']) >= 1


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_commitment_scope_direct(auth_client):
    """Get or create report with commitment_scope=direct includes only direct commitments"""

    with allure.step("Create task and direct commitment"):
        today = date.today().isoformat()
        task = create_task(auth_client, title="Task for direct scope")

        # Create commitment directly to this day
        auth_client.post('/api/commitments/soft', data={
            'target_type': 'task',
            'target_id': task['id'],
            'timeframe_kind': 'day',
            'reference_date': today
        })

    with allure.step("Get or create report with commitment_scope=direct"):
        response = auth_client.get(f'/api/reports/day/{today}', params={
            'commitment_scope': 'direct'
        })

    with allure.step("Verify commitments included"):
        assert response.status_code == 200
        assert 'commitments' in response
        assert 'stats' in response
        assert isinstance(response['commitments'], list)
        assert len(response['commitments']) == 1


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_commitment_scope_none(auth_client):
    """Get or create report with commitment_scope=none excludes commitments"""

    with allure.step("Get or create report with commitment_scope=none"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/day/{today}', params={
            'commitment_scope': 'none'
        })

    with allure.step("Verify commitments excluded"):
        assert response.status_code == 200
        assert 'commitments' not in response
        assert 'stats' not in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_full_true(auth_client):
    """Get or create report with full=true includes metadata"""

    with allure.step("Get or create report with full=true"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/day/{today}', params={'full': True})

    with allure.step("Verify metadata included"):
        assert response.status_code == 200
        assert 'id' in response
        assert 'user_id' in response
        assert 'timeframe_id' in response
        assert 'created_at' in response
        assert 'updated_at' in response
        assert 'timeframe' in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_full_false(auth_client):
    """Get or create report with full=false (default) excludes metadata"""

    with allure.step("Get or create report with full=false (default)"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/day/{today}')

    with allure.step("Verify metadata excluded"):
        assert response.status_code == 200
        assert 'id' not in response
        assert 'user_id' not in response
        assert 'timeframe_id' not in response
        assert 'created_at' not in response
        assert 'updated_at' not in response
        assert 'timeframe' not in response


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_invalid_kind(auth_client):
    """Get or create report with invalid kind returns 400"""

    with allure.step("Attempt to create report with invalid kind"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/invalid_kind/{today}', handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_invalid_date_format(auth_client):
    """Get or create report with invalid date format returns 400"""

    with allure.step("Attempt to create report with invalid date format"):
        response = auth_client.get('/api/reports/day/not-a-date', handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Reports')
@allure.story('Get or Create Report for Date')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_or_create_report_with_invalid_timezone(auth_client):
    """Get or create report with invalid timezone returns 400"""

    with allure.step("Attempt to create report with invalid timezone"):
        today = date.today().isoformat()
        response = auth_client.get(f'/api/reports/day/{today}', params={
            'timezone': 'Invalid/Timezone'
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400