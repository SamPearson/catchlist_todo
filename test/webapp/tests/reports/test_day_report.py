import pytest
from pages.reports.day_report_page import DayReportPage
import allure

@pytest.mark.devtest
@allure.feature("Daily Reports")
class TestDayReport:
    @pytest.fixture
    def page(self, login):
        return DayReportPage(login, "2025-06-24")  # Use a specific date for consistent testing

    @pytest.fixture
    def sample_report_data(self):
        return {
            'morning_notes': 'Test morning notes',
            'daily_plans': 'Test daily plans',
            'sleep_hours': '8',
            'prayer_rating': '7',
            'diet_adherence': '1',  # Maintained
            'work_adherence': '1',  # Completed
            'work_rpe': '6',
            'gains': 'Test gains',
            'gratitudes': 'Test gratitudes'
        }

    @allure.story("Create Report")
    def test_create_day_report(self, page, sample_report_data):
        """Test creating a new daily report"""
        page.fill_report(sample_report_data)
        page.save_report()

        # Reload the page to verify persistence
        page._visit(page.driver.current_url)

        # Verify some key fields
        assert page._find(page.morning_notes_locator).get_attribute('value') == sample_report_data['morning_notes']
        assert page._find(page.daily_plans_locator).get_attribute('value') == sample_report_data['daily_plans']
        assert page._find(page.sleep_hours_locator).get_attribute('value') == sample_report_data['sleep_hours']

    @allure.story("Update Report")
    def test_update_day_report(self, page, sample_report_data):
        """Test updating an existing daily report"""
        # First create a report
        page.fill_report(sample_report_data)
        page.save_report()

        # Update some fields
        updated_data = {
            'morning_notes': 'Updated morning notes',
            'sleep_hours': '9',
            'work_rpe': '8'
        }
        page.fill_report(updated_data)
        page.save_report()

        # Reload and verify updates
        page._visit(page.driver.current_url)
        assert page._find(page.morning_notes_locator).get_attribute('value') == updated_data['morning_notes']
        assert page._find(page.sleep_hours_locator).get_attribute('value') == updated_data['sleep_hours']
        assert page._find(page.work_rpe_locator).get_attribute('value') == updated_data['work_rpe']

    @allure.story("Navigation")
    def test_day_navigation(self, page):
        """Test navigating between days"""
        initial_url = page.driver.current_url

        # Navigate to next day
        page.navigate_to_next_day()
        assert page.driver.current_url != initial_url
        assert "2025-06-25" in page.driver.current_url

        # Navigate back
        page.navigate_to_previous_day()
        assert page.driver.current_url == initial_url