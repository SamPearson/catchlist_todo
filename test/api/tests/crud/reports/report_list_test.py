import pytest
import allure
from datetime import date
from utils.data_factories.entity_factory import create_report, create_timeframe, create_task



@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_returns_empty_array(auth_client):
    """New user with no reports gets empty array"""

    with allure.step("List reports for new user"):
        response = auth_client.get('/api/reports')

    with allure.step("Verify empty array returned"):
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_only_returns_users_own_reports(auth_client, secondary_auth_client):
    """Create reports for two different users, verify isolation"""

    with allure.step("Primary user creates report"):
        today = date.today().isoformat()
        primary_report = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        primary_id = primary_report['id']

    with allure.step("Secondary user creates report"):
        secondary_report = secondary_auth_client.get(f'/api/reports/week/{today}', params={'full': True})
        secondary_id = secondary_report['id']

    with allure.step("Primary user lists reports"):
        primary_list = auth_client.get('/api/reports')

    with allure.step("Secondary user lists reports"):
        secondary_list = secondary_auth_client.get('/api/reports')

    with allure.step("Verify primary user only sees own report"):
        primary_ids = [r.get('id') if 'id' in r else None for r in primary_list.json]
        # With commitment_scope=none (default), id might not be present
        # So get with full=true to verify isolation
        primary_full = auth_client.get('/api/reports', params={'full': True})
        primary_full_ids = [r['id'] for r in primary_full.json]
        assert primary_id in primary_full_ids
        assert secondary_id not in primary_full_ids

    with allure.step("Verify secondary user only sees own report"):
        secondary_full = secondary_auth_client.get('/api/reports', params={'full': True})
        secondary_full_ids = [r['id'] for r in secondary_full.json]
        assert secondary_id in secondary_full_ids
        assert primary_id not in secondary_full_ids


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_with_commitment_scope_none(auth_client):
    """List reports with commitment_scope=none (default) omits commitments and commitment stats"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        auth_client.get(f'/api/reports/day/{today}')

    with allure.step("List reports with default commitment_scope"):
        response = auth_client.get('/api/reports')

    with allure.step("Verify report returned"):
        assert response.status_code == 200
        assert len(response.json) >= 1
        report = response.json[0]

    with allure.step("Verify commitments field omitted"):
        assert 'commitments' not in report
        assert 'stats' not in report



@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_with_commitment_scope_window(auth_client):
    """List reports with commitment_scope=window includes commitments and stats"""

    with allure.step("Create week report"):
        today = date.today().isoformat()
        auth_client.get(f'/api/reports/week/{today}')

    with allure.step("Create tasks with commitments"):
        hard_day_task = create_task(auth_client, title="hard day task")
        hard_day_task_id = hard_day_task['id']
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": hard_day_task_id,
            "due_at": today
        })
        assert response.status_code == 201
        hard_day_commitment_id = response.json['id']

        soft_day_task = create_task(auth_client, title="soft day task")
        soft_day_task_id = soft_day_task['id']
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": soft_day_task_id,
            "timeframe_kind": "day",
            "reference_date": today
        })
        assert response.status_code == 201
        soft_day_commitment_id = response.json['id']

        soft_week_task = create_task(auth_client, title="soft week task")
        soft_week_task_id = soft_week_task['id']
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": soft_week_task_id,
            "timeframe_kind": "week",
            "reference_date": today
        })
        assert response.status_code == 201
        soft_week_commitment_id = response.json['id']

    with allure.step("List reports with commitment_scope=window"):
        response = auth_client.get('/api/reports', params={'commitment_scope': 'window'})
        assert response.status_code == 200
        assert len(response.json) == 1
        report = response.json[0]
        assert 'commitments' in report

    with allure.step("Verify commitments and stats fields included"):
        expected_ids = {hard_day_commitment_id, soft_day_commitment_id, soft_week_commitment_id}
        actual_ids = {c['id'] for c in report['commitments']}
        print(f"Expected IDs: {expected_ids}")
        print(f"Actual IDs: {actual_ids}")
        for id in expected_ids:
            assert id in actual_ids


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_with_commitment_scope_direct(auth_client):
    """List reports with commitment_scope=direct includes only direct commitments"""


    with allure.step("Create week report"):
        today = date.today().isoformat()
        auth_client.get(f'/api/reports/week/{today}')

    with allure.step("Create tasks with commitments"):
        hard_day_task = create_task(auth_client, title="hard day task")
        hard_day_task_id = hard_day_task['id']
        response = auth_client.post('/api/commitments/hard', {
            "target_type": "task",
            "target_id": hard_day_task_id,
            "due_at": today
        })
        assert response.status_code == 201
        hard_day_commitment_id = response.json['id']

        soft_day_task = create_task(auth_client, title="soft day task")
        soft_day_task_id = soft_day_task['id']
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": soft_day_task_id,
            "timeframe_kind": "day",
            "reference_date": today
        })
        assert response.status_code == 201
        soft_day_commitment_id = response.json['id']

        soft_week_task = create_task(auth_client, title="soft week task")
        soft_week_task_id = soft_week_task['id']
        response = auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": soft_week_task_id,
            "timeframe_kind": "week",
            "reference_date": today
        })
        assert response.status_code == 201
        soft_week_commitment_id = response.json['id']

    with allure.step("List reports with commitment_scope=window"):
        response = auth_client.get('/api/reports', params={'commitment_scope': 'direct'})
        assert response.status_code == 200
        assert len(response.json) == 1
        report = response.json[0]
        assert 'commitments' in report

    with allure.step("Verify commitments and stats fields included"):
        actual_ids = {c['id'] for c in report['commitments']}
        assert soft_week_commitment_id in actual_ids, "Soft week commitment should be included"
        assert hard_day_commitment_id not in actual_ids, "Hard day commitment should not be included"
        assert soft_day_commitment_id not in actual_ids, "Soft day commitment should not be included"


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_filters_by_timeframe_ids(auth_client):
    """Create reports for multiple timeframes, filter by comma-separated IDs"""

    with allure.step("Create multiple reports"):
        today = date.today().isoformat()
        report1 = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report2 = auth_client.get(f'/api/reports/week/{today}', params={'full': True})
        report3 = auth_client.get(f'/api/reports/month/{today}', params={'full': True})

        timeframe_id_1 = report1['timeframe_id']
        timeframe_id_2 = report2['timeframe_id']
        timeframe_id_3 = report3['timeframe_id']

    with allure.step("List reports filtered by two timeframe IDs"):
        response = auth_client.get('/api/reports', params={
            'timeframe_ids': f'{timeframe_id_1},{timeframe_id_2}',
            'full': True
        })

    with allure.step("Verify only filtered reports returned"):
        assert response.status_code == 200
        returned_ids = [r['timeframe_id'] for r in response.json]
        assert timeframe_id_1 in returned_ids
        assert timeframe_id_2 in returned_ids
        assert timeframe_id_3 not in returned_ids
        assert len(response.json) == 2


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_with_invalid_timeframe_ids_format(auth_client):
    """Invalid timeframe_ids format returns 400"""

    with allure.step("List reports with invalid timeframe_ids format"):
        response = auth_client.get('/api/reports', params={
            'timeframe_ids': 'invalid,not-a-number'
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_with_nonexistent_timeframe_ids(auth_client):
    """Nonexistent timeframe_ids returns empty or filtered results"""

    with allure.step("Create one report"):
        today = date.today().isoformat()
        auth_client.get(f'/api/reports/day/{today}')

    with allure.step("List reports with nonexistent timeframe IDs"):
        response = auth_client.get('/api/reports', params={
            'timeframe_ids': '999999,888888'
        })

    with allure.step("Verify empty array returned"):
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_with_full_true(auth_client):
    """List reports with full=true includes metadata fields"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        auth_client.get(f'/api/reports/day/{today}')

    with allure.step("List reports with full=true"):
        response = auth_client.get('/api/reports', params={'full': True})

    with allure.step("Verify metadata fields included"):
        assert response.status_code == 200
        assert len(response.json) >= 1
        report = response.json[0]
        assert 'id' in report
        assert 'user_id' in report
        assert 'timeframe_id' in report
        assert 'created_at' in report
        assert 'updated_at' in report
        assert 'timeframe' in report


@allure.feature('Reports')
@allure.story('List Reports')
@pytest.mark.reports
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_reports_with_full_false(auth_client):
    """List reports with full=false (default) excludes metadata fields"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        auth_client.get(f'/api/reports/day/{today}')

    with allure.step("List reports with full=false (default)"):
        response = auth_client.get('/api/reports')

    with allure.step("Verify metadata fields excluded"):
        assert response.status_code == 200
        assert len(response.json) >= 1
        report = response.json[0]
        assert 'id' not in report
        assert 'user_id' not in report
        assert 'timeframe_id' not in report
        assert 'created_at' not in report
        assert 'updated_at' not in report
        assert 'timeframe' not in report

    with allure.step("Verify text fields present"):
        assert 'plan' in report
        assert 'reason' in report
        assert 'pre_notes' in report
        assert 'post_notes' in report