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

    # Navbar visibility checks
    def is_navbar_loaded(self):
        """Check if the navbar has loaded by verifying the brand link is visible"""
        return self._is_active(self.navbar_brand_link_locator, timeout=3)

    def is_register_button_visible(self):
        """Check if the register button is visible (logged-out state)"""
        return self._is_active(self.navbar_register_button_locator, timeout=2)

    def is_login_button_visible(self):
        """Check if the login button is visible (logged-out state)"""
        return self._is_active(self.navbar_login_button_locator, timeout=2)

    def is_logout_button_visible(self):
        """Check if the logout button is visible (logged-in state)"""
        return self._is_active(self.navbar_logout_button_locator, timeout=2)

    def is_account_button_visible(self):
        """Check if the account button is visible (logged-in state)"""
        return self._is_active(self.navbar_account_button_locator, timeout=2)

    def is_desk_link_visible(self):
        """Check if the desk navigation link is visible (logged-in state)"""
        return self._is_active(self.navbar_desk_link_locator, timeout=2)

    def is_tasks_link_visible(self):
        """Check if the tasks navigation link is visible (logged-in state)"""
        return self._is_active(self.navbar_tasks_link_locator, timeout=2)

    def is_projects_link_visible(self):
        """Check if the projects navigation link is visible (logged-in state)"""
        return self._is_active(self.navbar_projects_link_locator, timeout=2)

    def is_routines_link_visible(self):
        """Check if the routines navigation link is visible (logged-in state)"""
        return self._is_active(self.navbar_routines_link_locator, timeout=2)

    def is_reports_link_visible(self):
        """Check if the reports navigation link is visible (logged-in state)"""
        return self._is_active(self.navbar_reports_link_locator, timeout=2)

    # Navbar interactions
    def click_navbar_register(self):
        """Click the register button in the navbar"""
        self._click(self.navbar_register_button_locator)

    def click_navbar_login(self):
        """Click the login button in the navbar"""
        self._click(self.navbar_login_button_locator)

    def click_navbar_logout(self):
        """Click the logout button in the navbar"""
        self._click(self.navbar_logout_button_locator)

    def click_navbar_account(self):
        """Click the account button in the navbar"""
        self._click(self.navbar_account_button_locator)

    def click_navbar_desk(self):
        """Click the desk link in the navbar"""
        self._click(self.navbar_desk_link_locator)

    def click_navbar_tasks(self):
        """Click the tasks link in the navbar"""
        self._click(self.navbar_tasks_link_locator)

    def click_navbar_projects(self):
        """Click the projects link in the navbar"""
        self._click(self.navbar_projects_link_locator)

    def click_navbar_routines(self):
        """Click the routines link in the navbar"""
        self._click(self.navbar_routines_link_locator)

    def click_navbar_reports(self):
        """Click the reports link in the navbar"""
        self._click(self.navbar_reports_link_locator)

    def click_navbar_brand(self):
        """Click the navbar brand link (usually goes to home)"""
        self._click(self.navbar_brand_link_locator)

    # High-level state verification methods
    def verify_logged_out_navbar_state(self):
        """
        Verify that the navbar shows the correct elements for a logged-out user.
        
        Returns:
            bool: True if navbar is in correct logged-out state
        """
        return (self.is_navbar_loaded() and 
                self.is_register_button_visible() and 
                self.is_login_button_visible() and 
                not self.is_logout_button_visible())

    def verify_logged_in_navbar_state(self):
        """
        Verify that the navbar shows the correct elements for a logged-in user.
        
        Returns:
            bool: True if navbar is in correct logged-in state
        """
        return (self.is_navbar_loaded() and 
                self.is_logout_button_visible() and 
                self.is_account_button_visible() and 
                self.is_desk_link_visible() and 
                self.is_tasks_link_visible() and 
                self.is_projects_link_visible())

    def verify_all_logged_in_nav_links_visible(self):
        """
        Verify that all main navigation links are visible for logged-in users.
        
        Returns:
            bool: True if all navigation links are visible
        """
        return (self.is_desk_link_visible() and 
                self.is_tasks_link_visible() and 
                self.is_projects_link_visible())
