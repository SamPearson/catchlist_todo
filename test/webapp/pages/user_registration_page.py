from pages.base_app_page import BaseAppPage
from pages.base_page import locator_from_testid


class RegistrationPage(BaseAppPage):
    username_input_locator = locator_from_testid("register-username-input")
    password_input_locator = locator_from_testid("register-password-input")
    submit_button_locator = locator_from_testid("register-submit-button")
    success_message_locator = locator_from_testid("register-success-message")
    error_message_locator = locator_from_testid("register-error-message")
    login_link_locator = locator_from_testid("register-login-link")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/auth/register")

    def register_new_user(self, username, password):
        """Register a new user account"""
        self._type(self.username_input_locator, username)
        self._type(self.password_input_locator, password)
        self._click(self.submit_button_locator)
        
        # Wait for success message and redirect
        self._wait_for_url('contains', '/auth/login', timeout=10)

    def has_error_message(self):
        """Check if an error message is displayed"""
        return self._is_displayed(self.error_message_locator, timeout=2)
