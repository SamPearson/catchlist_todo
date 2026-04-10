import pytest
import allure
from datetime import date


@allure.feature('Reports')
@allure.story('Smoke Tests')
@pytest.mark.reports
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_or_create_report_for_today(auth_client):
    """Get or create report for today's date"""

    with allure.step("Prepare today's date"):
        today = date.today().isoformat()

    with allure.step("Get or create report for today"):
        response = auth_client.get(f'/api/reports/day/{today}')

    with allure.step("Verify report structure"):
        assert response.status_code == 200
        assert 'plan' in response
        assert 'reason' in response
        assert 'pre_notes' in response
        assert 'post_notes' in response


@allure.feature('Reports')
@allure.story('Smoke Tests')
@pytest.mark.reports
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_reports(auth_client):
    """List reports returns array with created report"""

    with allure.step("Create a report"):
        today = date.today().isoformat()
        auth_client.get(f'/api/reports/day/{today}')

    with allure.step("List all reports"):
        response = auth_client.get('/api/reports')

    with allure.step("Verify report appears in list"):
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) >= 1


@allure.feature('Reports')
@allure.story('Smoke Tests')
@pytest.mark.reports
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_report_by_id(auth_client):
    """Get report by ID returns the report"""

    with allure.step("Create a report and get ID"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Get report by ID"):
        response = auth_client.get(f'/api/reports/{report_id}')

    with allure.step("Verify report returned"):
        assert response.status_code == 200
        assert 'plan' in response
        assert 'reason' in response


@allure.feature('Reports')
@allure.story('Smoke Tests')
@pytest.mark.reports
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_report_plan(auth_client):
    """Update report plan field"""

    with allure.step("Create a report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Update report plan"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'Complete smoke tests for Reports API'
        })

    with allure.step("Verify plan updated"):
        assert response.status_code == 200
        assert response['plan'] == 'Complete smoke tests for Reports API'


@allure.feature('Reports')
@allure.story('Smoke Tests')
@pytest.mark.reports
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_report(auth_client):
    """Delete report returns 204"""

    with allure.step("Create a report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Delete report"):
        response = auth_client.delete(f'/api/reports/{report_id}', handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204

    with allure.step("Verify report actually deleted"):
        get_response = auth_client.get(f'/api/reports/{report_id}', handle_response=False)
        assert get_response.status_code == 404