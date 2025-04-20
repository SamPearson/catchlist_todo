from pages.base_page import BasePage, testid_locator


class BaseAppPage(BasePage):
    home_link_locator = testid_locator("home-link")
    login_link_locator = testid_locator("login-link")
    logout_link_locator = testid_locator("logout-link")
    register_link_locator = testid_locator("register-link")

    def __init__(self, driver):
        super().__init__(driver)
