from pages.base_app_page import BaseAppPage
from pages.base_page import testid_locator


class LoginPage(BaseAppPage):
    username_field_locator = testid_locator("username-input")
    password_field_locator = testid_locator("password-input")
    login_button_locator = testid_locator("login-button")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/login")

    def login(self, username, password):
        self._click(self.login_link_locator)
        self._type(self.username_field_locator, username)
        self._type(self.password_field_locator, password)
        self._click(self.login_button_locator)

        # some assertions to make sure we are past the login page
        self.wait_for_url('contains', '/desk')
        assert self._is_active(self.logout_link_locator, 5), "Could not find the logout button after logging in"

