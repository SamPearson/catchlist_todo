import pytest
import allure
from datetime import date
from utils.data_factories.entity_factory import create_task


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_report_returns_full_object(auth_client):
    """Get report returns full object with all fields"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Get report by ID"):
        response = auth_client.get(f'/api/reports/{report_id}')

    with allure.step("Verify all fields present"):
        assert response.status_code == 200
        assert 'plan' in response
        assert 'reason' in response
        assert 'pre_notes' in response
        assert 'post_notes' in response
        assert 'label' in response
        assert 'report_type' in response


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_report_with_commitment_scope_window(auth_client):
    """Get report with commitment_scope=window (default) includes commitments and stats"""

    with allure.step("Create report with commitment"):
        today = date.today().isoformat()
        task = create_task(auth_client, title="Task for get test")

        # Create commitment
        auth_client.post('/api/commitments/soft', data={
            'target_type': 'task',
            'target_id': task['id'],
            'timeframe_kind': 'day',
            'reference_date': today
        })

        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Get report with default commitment_scope"):
        response = auth_client.get(f'/api/reports/{report_id}')

    with allure.step("Verify commitments and stats included"):
        assert response.status_code == 200
        assert 'commitments' in response
        assert 'stats' in response
        assert isinstance(response['commitments'], list)
        assert len(response['commitments']) >= 1
        assert isinstance(response['stats'], dict)


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_report_with_commitment_scope_direct(auth_client):
    """Get report with commitment_scope=direct includes only direct commitments"""

    with allure.step("Create weekly report with commitments"):
        today = date.today().isoformat()

        # Create tasks
        week_task = create_task(auth_client, title="Week task")
        day_task = create_task(auth_client, title="Day task")

        # Create commitment directly to week
        week_commitment = auth_client.post('/api/commitments/soft', data={
            'target_type': 'task',
            'target_id': week_task['id'],
            'timeframe_kind': 'week',
            'reference_date': today
        })
        week_commitment_id = week_commitment['id']

        # Create commitment to day within week
        day_commitment = auth_client.post('/api/commitments/soft', data={
            'target_type': 'task',
            'target_id': day_task['id'],
            'timeframe_kind': 'day',
            'reference_date': today
        })
        day_commitment_id = day_commitment['id']

        created = auth_client.get(f'/api/reports/week/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Get report with commitment_scope=direct"):
        response = auth_client.get(f'/api/reports/{report_id}', params={
            'commitment_scope': 'direct'
        })

    with allure.step("Verify only direct commitments included"):
        assert response.status_code == 200
        assert 'commitments' in response
        commitment_ids = [c['id'] for c in response['commitments']]
        assert week_commitment_id in commitment_ids
        assert day_commitment_id not in commitment_ids


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_report_with_commitment_scope_none(auth_client):
    """Get report with commitment_scope=none excludes commitments and stats"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Get report with commitment_scope=none"):
        response = auth_client.get(f'/api/reports/{report_id}', params={
            'commitment_scope': 'none'
        })

    with allure.step("Verify commitments and stats excluded"):
        assert response.status_code == 200
        assert 'commitments' not in response
        assert 'stats' not in response


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_report_with_full_true(auth_client):
    """Get report with full=true includes metadata"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Get report with full=true"):
        response = auth_client.get(f'/api/reports/{report_id}', params={'full': True})

    with allure.step("Verify metadata included"):
        assert response.status_code == 200
        assert 'id' in response
        assert 'user_id' in response
        assert 'timeframe_id' in response
        assert 'created_at' in response
        assert 'updated_at' in response
        assert 'timeframe' in response


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_report_with_full_false(auth_client):
    """Get report with full=false (default) excludes metadata"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Get report with full=false (default)"):
        response = auth_client.get(f'/api/reports/{report_id}')

    with allure.step("Verify metadata excluded"):
        assert response.status_code == 200
        assert 'id' not in response
        assert 'user_id' not in response
        assert 'timeframe_id' not in response
        assert 'created_at' not in response
        assert 'updated_at' not in response
        assert 'timeframe' not in response

    with allure.step("Verify text fields present"):
        assert 'plan' in response
        assert 'reason' in response
        assert 'pre_notes' in response
        assert 'post_notes' in response


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_report(auth_client):
    """Get nonexistent report returns 404"""

    with allure.step("Attempt to get nonexistent report"):
        response = auth_client.get('/api/reports/999999', handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Reports')
@allure.story('Get Report by ID')
@pytest.mark.reports
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_report(auth_client, secondary_auth_client):
    """Get another user's report returns 404"""

    with allure.step("Secondary user creates report"):
        today = date.today().isoformat()
        secondary_report = secondary_auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        secondary_report_id = secondary_report['id']

    with allure.step("Primary user attempts to get secondary user's report"):
        response = auth_client.get(f'/api/reports/{secondary_report_id}', handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404