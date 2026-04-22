from pages.base_app_page import BaseAppPage
from pages.base_page import locator_from_testid


class LoginPage(BaseAppPage):
    username_input_locator = locator_from_testid("login-username-input")
    password_input_locator = locator_from_testid("login-password-input")
    submit_button_locator = locator_from_testid("login-submit-button")
    error_message_locator = locator_from_testid("login-error-message")
    register_link_locator = locator_from_testid("login-register-link")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/auth/login")

    def login(self, username, password):
        """Log in with provided credentials"""
        self._type(self.username_input_locator, username)
        self._type(self.password_input_locator, password)
        self._click(self.submit_button_locator)

        # Wait for redirect to home page after successful login
        self._wait_for_url('is', self.driver.base_url + '/', timeout=10)
        
        # Verify we're logged in by checking for logout button in navbar
        assert self._is_active(self.navbar_logout_button_locator, 5), "Could not find the logout button after logging in"

    def has_error_message(self):
        """Check if an error message is displayed"""
        return self._is_displayed(self.error_message_locator, timeout=2)

