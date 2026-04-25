from pages.base_app_page import BaseAppPage
from pages.base_page import locator_from_testid


class DashboardPage(BaseAppPage):
    # Card containers
    desk_card_locator = locator_from_testid("dashboard-desk-card")
    tasks_card_locator = locator_from_testid("dashboard-tasks-card")
    projects_card_locator = locator_from_testid("dashboard-projects-card")
    routines_card_locator = locator_from_testid("dashboard-routines-card")
    reports_card_locator = locator_from_testid("dashboard-reports-card")
    account_card_locator = locator_from_testid("dashboard-account-card")

    # Buttons
    desk_button_locator = locator_from_testid("dashboard-desk-button")
    tasks_button_locator = locator_from_testid("dashboard-tasks-button")
    projects_button_locator = locator_from_testid("dashboard-projects-button")
    routines_button_locator = locator_from_testid("dashboard-routines-button")
    reports_button_locator = locator_from_testid("dashboard-reports-button")
    account_button_locator = locator_from_testid("dashboard-account-button")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/")

    def navigate_to_tasks_demo(self):
        """Navigate to the tasks component demo"""
        self._click(self.tasks_button_locator)
        self._wait_for_url('contains', '/component-demo/tasks')

    def navigate_to_account(self):
        """Navigate to the account settings page"""
        self._click(self.account_button_locator)
        self._wait_for_url('contains', '/auth/account')

    def is_card_visible(self, card_name):
        """Check if a specific dashboard card is visible"""
        card_locators = {
            'desk': self.desk_card_locator,
            'tasks': self.tasks_card_locator,
            'projects': self.projects_card_locator,
            'routines': self.routines_card_locator,
            'reports': self.reports_card_locator,
            'account': self.account_card_locator,
        }
        return self._is_displayed(card_locators[card_name], timeout=2)