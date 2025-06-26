import pytest
import allure
from datetime import date
from utils.data_factories.reports.day_report_factory import DayReportFactory


@allure.feature('Day Reports')
@allure.story('CRUD Operations')
@pytest.mark.day_report
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_day_report(auth_client):
    """Test creating a new day report"""
    with allure.step("Prepare test data"):
        data = {
            "date": "2025-06-03",
            "sleep_hours": 7.5,
            "prayer_rating": 8,
            "notes": "Productive day, stayed focused"
        }

    with allure.step("Create new day report"):
        response = auth_client.post('/api/reports/day', data)

    with allure.step("Verify response"):
        assert 'id' in response
        assert response['date'] == data['date']
        assert response['notes'] == data['notes']


@allure.feature('Day Reports')
@allure.story('CRUD Operations')
@pytest.mark.day_report
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_day_report(auth_client):
    """Test updating an existing day report"""
    with allure.step("Create initial report"):
        initial_data = {
            "date": "2025-06-03",
            "sleep_hours": 7.5,
            "prayer_rating": 8,
            "notes": "Initial notes"
        }
        create_response = auth_client.post('/api/reports/day', initial_data)
        report_id = create_response['id']

    with allure.step("Update the report"):
        update_data = {
            "sleep_hours": 8.0,
            "prayer_rating": 9,
            "notes": "Updated notes"
        }
        update_response = auth_client.put(f'/api/reports/day/{report_id}', update_data)

    with allure.step("Verify updates"):
        assert update_response['id'] == report_id
        assert update_response['sleep_hours'] == 8.0
        assert update_response['prayer_rating'] == 9
        assert update_response['notes'] == "Updated notes"
        assert update_response['date'] == initial_data['date']


@allure.feature('Day Reports')
@allure.story('CRUD Operations')
@pytest.mark.day_report
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_day_report(auth_client):
    """Test deleting a day report"""
    with allure.step("Create report to be deleted"):
        data = {
            "date": "2025-06-03",
            "sleep_hours": 7.5,
            "prayer_rating": 8,
            "notes": "To be deleted"
        }
        create_response = auth_client.post('/api/reports/day', data)
        report_id = create_response['id']

    with allure.step("Delete the report"):
        delete_response = auth_client.delete(f'/api/reports/day/{report_id}', handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify report is deleted"):
        with pytest.raises(Exception) as exc_info:
            auth_client.get(f'/api/reports/day/2025-06-03')
        assert "404" in str(exc_info.value)


@allure.feature('Day Reports')
@allure.story('CRUD Operations')
@pytest.mark.day_report
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_day_report(auth_client):
    """Test retrieving a specific day report"""
    with allure.step("Create test report"):
        data = {
            "date": "2025-06-03",
            "sleep_hours": 7.5,
            "prayer_rating": 8,
            "notes": "Test report"
        }
        auth_client.post('/api/reports/day', data)

    with allure.step("Retrieve the report"):
        response = auth_client.get('/api/reports/day/2025-06-03')
        assert response['notes'] == "Test report"
        assert response['date'] == "2025-06-03"


@allure.feature('Day Reports')
@allure.story('CRUD Operations')
@pytest.mark.day_report
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_day_reports(auth_client):
    """Test retrieving all day reports"""
    with allure.step("Create multiple test reports"):
        reports = [
            {
                "date": "2025-06-03",
                "sleep_hours": 7.5,
                "prayer_rating": 8,
                "notes": "Test report 1"
            },
            {
                "date": "2025-06-04",
                "sleep_hours": 8.0,
                "prayer_rating": 7,
                "notes": "Test report 2"
            }
        ]
        for report in reports:
            auth_client.post('/api/reports/day', report)

    with allure.step("Retrieve all reports"):
        response = auth_client.get('/api/reports/day')
        assert isinstance(response, list)
        assert len(response) >= 2