from pages.base_app_page import BaseAppPage
from pages.base_page import testid_locator
from selenium.webdriver.common.by import By


class DeskPage(BaseAppPage):
    # username_field_locator = testid_locator("username-input")
    # password_field_locator = testid_locator("password-input")
    # login_button_locator = testid_locator("login-button")
    kaboom_button = (By.ID, 'kaboom-button')

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/desk")

    def kaboom(self):
        self._click(self.kaboom_button)

