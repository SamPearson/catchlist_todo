import pytest
import allure
from datetime import date
from utils.data_factories.entity_factory import create_task


@allure.feature('Reports')
@allure.story('Delete Report')
@pytest.mark.reports
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_report_returns_204(auth_client):
    """Delete report returns 204 No Content"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Delete report"):
        response = auth_client.delete(f'/api/reports/{report_id}', handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204


@allure.feature('Reports')
@allure.story('Delete Report')
@pytest.mark.reports
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_report_actually_removes_it(auth_client):
    """Delete report actually removes it, verify GET returns 404 afterward"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Delete report"):
        response = auth_client.delete(f'/api/reports/{report_id}', handle_response=False)
        assert response.status_code == 204

    with allure.step("Verify report no longer exists"):
        get_response = auth_client.get(f'/api/reports/{report_id}', handle_response=False)
        assert get_response.status_code == 404


@allure.feature('Reports')
@allure.story('Delete Report')
@pytest.mark.reports
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_report_does_not_delete_timeframe(auth_client):
    """Delete report does NOT delete timeframe, verify timeframe still exists"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']
        timeframe_id = created['timeframe_id']

    with allure.step("Delete report"):
        response = auth_client.delete(f'/api/reports/{report_id}', handle_response=False)
        assert response.status_code == 204

    with allure.step("Verify timeframe still exists"):
        timeframe_response = auth_client.get(f'/api/timeframes/{timeframe_id}')
        assert timeframe_response.status_code == 200


@allure.feature('Reports')
@allure.story('Delete Report')
@pytest.mark.reports
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_report_does_not_delete_commitments(auth_client):
    """Delete report does NOT delete commitments, verify commitments remain"""

    with allure.step("Create report with commitment"):
        today = date.today().isoformat()
        task = create_task(auth_client, title="Task for delete test")

        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']
        timeframe_id = created['timeframe_id']

        # Create commitment
        commitment = auth_client.post('/api/commitments/soft', data={
            'target_type': 'task',
            'target_id': task['id'],
            'timeframe_kind': 'day',
            'reference_date': today
        })
        commitment_id = commitment['id']

    with allure.step("Delete report"):
        response = auth_client.delete(f'/api/reports/{report_id}', handle_response=False)
        assert response.status_code == 204

    with allure.step("Verify commitment still exists"):
        commitment_response = auth_client.get(f'/api/commitments/{commitment_id}')
        assert commitment_response.status_code == 200
        assert commitment_response['id'] == commitment_id
        assert commitment_response['timeframe_id'] == timeframe_id


@allure.feature('Reports')
@allure.story('Delete Report')
@pytest.mark.reports
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_report_does_not_delete_checkins(auth_client):
    """Delete report does NOT delete checkins targeting report, verify checkins remain"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        # Create checkin targeting the report
        checkin = auth_client.post('/api/checkins', data={
            'target_type': 'report',
            'target_id': report_id,
            'note': 'Checkin for report delete test'
        })
        checkin_id = checkin['id']

    with allure.step("Delete report"):
        response = auth_client.delete(f'/api/reports/{report_id}', handle_response=False)
        assert response.status_code == 204

    with allure.step("Verify checkin still exists"):
        checkin_response = auth_client.get(f'/api/checkins/{checkin_id}')
        assert checkin_response.status_code == 200
        assert checkin_response['id'] == checkin_id
        assert checkin_response['target_type'] == 'report'
        assert checkin_response['target_id'] == report_id


@allure.feature('Reports')
@allure.story('Delete Report')
@pytest.mark.reports
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_report(auth_client):
    """Delete nonexistent report returns 404"""

    with allure.step("Attempt to delete nonexistent report"):
        response = auth_client.delete('/api/reports/999999', handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Reports')
@allure.story('Delete Report')
@pytest.mark.reports
@pytest.mark.delete
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_users_report(auth_client, secondary_auth_client):
    """Delete another user's report returns 404"""

    with allure.step("Secondary user creates report"):
        today = date.today().isoformat()
        secondary_report = secondary_auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        secondary_report_id = secondary_report['id']

    with allure.step("Primary user attempts to delete secondary user's report"):
        response = auth_client.delete(f'/api/reports/{secondary_report_id}', handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404

    with allure.step("Verify secondary user's report still exists"):
        secondary_check = secondary_auth_client.get(f'/api/reports/{secondary_report_id}')
        assert secondary_check.status_code == 200