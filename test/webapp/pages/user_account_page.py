from pages.base_app_page import BaseAppPage
from pages.base_page import testid_locator


class AccountPage(BaseAppPage):
    # Locators
    delete_button_locator = testid_locator("delete-account-btn")
    confirm_password_input_locator = testid_locator("delete-account-password-input")
    confirm_delete_button_locator = testid_locator("delete-account-confirm-btn")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/account")

    def delete_account(self, password):
        self._click(self.delete_button_locator)
        self._wait_until(lambda d: self._is_displayed(self.confirm_password_input_locator))
        self._type(self.confirm_password_input_locator, password)
        self._click(self.confirm_delete_button_locator)
        # Wait for redirect to login page
        self.wait_for_url('contains', '/login')
