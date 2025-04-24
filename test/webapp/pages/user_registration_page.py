from pages.base_app_page import BaseAppPage
from pages.base_page import testid_locator


class RegistrationPage(BaseAppPage):
    username_input_locator = testid_locator("register-username")
    password_input_locator = testid_locator("register-password")
    password_confirmation_locator = testid_locator("register-confirm-password")
    register_button_locator = testid_locator("register-submit")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/register")

    def register_new_user(self, username, password):
        self._type(self.username_input_locator, username)
        self._type(self.password_input_locator, password)
        self._type(self.password_confirmation_locator, password)
        self._click(self.register_button_locator)
        # Wait for redirect to login page
        self.wait_for_url('contains', '/login')
