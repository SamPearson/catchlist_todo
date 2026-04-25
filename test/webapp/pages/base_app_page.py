from pages.base_page import BasePage, locator_from_testid


class BaseAppPage(BasePage):
    home_link_locator = locator_from_testid("home-link")
    login_link_locator = locator_from_testid("login-link")
    logout_link_locator = locator_from_testid("logout-link")
    # Navbar brand
    navbar_brand_link_locator = locator_from_testid("navbar-brand-link")
    navbar_burger_locator = locator_from_testid("navbar-burger")
    
    # Logged-in navigation links
    navbar_desk_link_locator = locator_from_testid("navbar-desk-link")
    navbar_tasks_link_locator = locator_from_testid("navbar-tasks-link")
    navbar_projects_link_locator = locator_from_testid("navbar-projects-link")
    navbar_routines_link_locator = locator_from_testid("navbar-routines-link")
    navbar_reports_link_locator = locator_from_testid("navbar-reports-link")
    
    # Logged-in buttons
    navbar_account_button_locator = locator_from_testid("navbar-account-button")
    navbar_logout_button_locator = locator_from_testid("navbar-logout-button")
    
    # Logged-out buttons
    navbar_register_button_locator = locator_from_testid("navbar-register-button")
    navbar_login_button_locator = locator_from_testid("navbar-login-button")

    def __init__(self, driver):
        super().__init__(driver)
