from pages.base_app_page import BaseAppPage
from pages.base_page import locator_from_testid


class LandingPage(BaseAppPage):
    landing_login_button_locator = locator_from_testid("landing-login-button")
    landing_register_button_locator = locator_from_testid("landing-register-button")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/")

    def click_login(self):
        """Click the login button on the landing page"""
        self._click(self.landing_login_button_locator)

    def click_register(self):
        """Click the register button on the landing page"""
        self._click(self.landing_register_button_locator)