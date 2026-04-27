import pytest
import allure
import random
from pages.login_page import LoginPage
from pages.user_registration_page import RegistrationPage
from pages.user_account_page import AccountPage
from pages.base_app_page import BaseAppPage


@allure.feature('Authentication')
@allure.story('User Registration')
@pytest.mark.auth
class TestUserRegistration:
    """Tests for user registration flow"""

    @pytest.mark.smoke
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_new_user_success(self, unauthenticated_driver, api_client):
        """Test successful user registration"""
        # Generate unique credentials
        rand_int = random.randint(0, 99999)
        username = f"test_reg_user{rand_int}"
        password = f"TestPass{rand_int}!"

        try:
            with allure.step("Register new user via UI"):
                page = RegistrationPage(unauthenticated_driver)
                page.register_new_user(username, password)

            with allure.step("Verify redirect to login page"):
                assert '/auth/login' in unauthenticated_driver.current_url, \
                    "User was not redirected to login page after registration"

        finally:
            # Cleanup: Delete the user via API
            try:
                api_client.login_user(username, password)
                api_client.delete_user(password)
            except Exception as e:
                print(f"Failed to delete test user {username}: {e}")


    @allure.severity(allure.severity_level.NORMAL)
    def test_register_duplicate_username(self, unauthenticated_driver, api_client):
        """Test that registering with an existing username shows an error"""
        # Create a user via API first
        rand_int = random.randint(0, 99999)
        username = f"test_dup_user{rand_int}"
        password = f"TestPass{rand_int}!"

        try:
            with allure.step("Create existing user via API"):
                api_client.register_user(username, password)

            with allure.step("Attempt to register duplicate username via UI"):
                page = RegistrationPage(unauthenticated_driver)
                page._type(page.username_input_locator, username)
                page._type(page.password_input_locator, password)
                page._click(page.submit_button_locator)

            with allure.step("Verify error message is displayed"):
                assert page._is_active(page.error_message_locator, timeout=5), \
                    "Error message not displayed for duplicate username"

        finally:
            # Cleanup
            try:
                api_client.login_user(username, password)
                api_client.delete_user(password)
            except Exception as e:
                print(f"Failed to delete test user {username}: {e}")



@allure.feature('Authentication')
@allure.story('User Login')
@pytest.mark.auth
class TestUserLogin:
    """Tests for user login flow"""

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_success(self, unauthenticated_driver, api_client):
        """Test successful login with valid credentials"""
        # Create user via API
        rand_int = random.randint(0, 99999)
        username = f"test_login_user{rand_int}"
        password = f"TestPass{rand_int}!"

        try:
            with allure.step("Create test user via API"):
                api_client.register_user(username, password)

            with allure.step("Login via UI"):
                page = LoginPage(unauthenticated_driver)
                page.login(username, password)

            with allure.step("Verify redirect to home page"):
                assert unauthenticated_driver.current_url == unauthenticated_driver.base_url + '/', \
                    "User was not redirected to home page after login"

        finally:
            # Cleanup: Delete user via API
            try:
                api_client.login_user(username, password)
                api_client.delete_user(password)
            except Exception as e:
                print(f"Failed to delete test user {username}: {e}")

    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_invalid_credentials(self, unauthenticated_driver):
        """Test that invalid credentials show an error"""
        with allure.step("Attempt login with invalid credentials"):
            page = LoginPage(unauthenticated_driver)
            page._type(page.username_input_locator, "nonexistent_user")
            page._type(page.password_input_locator, "wrong_password")
            page._click(page.submit_button_locator)

        with allure.step("Verify error message is displayed"):
            assert page._is_active(page.error_message_locator, timeout=5), \
                "Error message not displayed for invalid credentials"



@allure.feature('Navigation')
@allure.story('Navbar Authentication State')
@pytest.mark.auth
class TestNavbarAuthentication:
    """Tests for navbar changes based on authentication state"""

    @allure.severity(allure.severity_level.NORMAL)
    def test_navbar_logged_out_state(self, unauthenticated_driver):
        """Test that navbar shows correct elements when logged out"""
        driver = unauthenticated_driver

        with allure.step("Navigate to home page"):
            driver.get(driver.base_url)

        page = BaseAppPage(driver)

        with allure.step("Verify navbar loads"):
            assert page.is_navbar_loaded(), \
                "Navbar did not load"

        with allure.step("Verify logged-out buttons are visible"):
            assert page.is_register_button_visible(), \
                "Register button not visible when logged out"
            assert page.is_login_button_visible(), \
                "Login button not visible when logged out"

        with allure.step("Verify logged-in elements are not visible"):
            assert not page.is_logout_button_visible(), \
                "Logout button should not be visible when logged out"
            assert not page.is_desk_link_visible(), \
                "Desk link not visible when logged in"
            assert not page.is_tasks_link_visible(), \
                "Tasks link not visible when logged in"
            assert not page.is_projects_link_visible(), \
                "Projects link not visible when logged in"


    @allure.severity(allure.severity_level.NORMAL)
    def test_navbar_logged_in_state(self, authenticated_driver):
        """Test that navbar shows correct elements when logged in"""

        page = BaseAppPage(authenticated_driver)

        with allure.step("Verify logged-in buttons are visible"):
            assert page.is_logout_button_visible(), \
                "Logout button not visible when logged in"
            assert page.is_account_button_visible(), \
                "Account button not visible when logged in"

        with allure.step("Verify logged-in navigation links are visible"):
            assert page.is_desk_link_visible(), \
                "Desk link not visible when logged in"
            assert page.is_tasks_link_visible(), \
                "Tasks link not visible when logged in"
            assert page.is_projects_link_visible(), \
                "Projects link not visible when logged in"



@allure.feature('Account Management')
@allure.story('Account Access')
@pytest.mark.auth
class TestAccountManagement:
    """Tests for account management page access and functionality"""

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_access_account_page_when_logged_in(self, authenticated_driver):
        """Test that authenticated users can access the account page"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        with allure.step("Verify on account page"):
            assert '/auth/account' in authenticated_driver.current_url, \
                "Did not navigate to account page"

        with allure.step("Verify username is displayed"):
            username = page.get_username()
            assert username, "Username not displayed on account page"


    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_profile_display_name(self, authenticated_driver):
        """Test updating profile display name"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        with allure.step("Get original display name"):
            original_name = page.get_display_name()

        with allure.step("Update display name"):
            new_name = "Updated Test Name"
            page.update_profile(name=new_name)

        with allure.step("Verify display name was updated"):
            updated_name = page.get_display_name()
            assert updated_name == new_name, \
                f"Display name not updated. Expected '{new_name}', got '{updated_name}'"
            assert updated_name != original_name, \
                "Display name did not change from original value"

    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_profile_timezone(self, authenticated_driver):
        """Test updating profile timezone"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        with allure.step("Get original timezone"):
            original_timezone = page.get_timezone()

        with allure.step("Update timezone"):
            new_timezone = "America/Los_Angeles"
            page.update_profile(timezone=new_timezone)

        with allure.step("Verify timezone was updated"):
            updated_timezone = page.get_timezone()
            assert new_timezone in updated_timezone, \
                f"Timezone not updated. Expected '{new_timezone}' in '{updated_timezone}'"
            assert updated_timezone != original_timezone, \
                "Timezone did not change from original value"

    @allure.severity(allure.severity_level.MINOR)
    def test_cancel_profile_edit(self, authenticated_driver):
        """Test canceling profile edit doesn't save changes"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        with allure.step("Get original display name"):
            original_name = page.get_display_name()

        with allure.step("Start editing and make changes"):
            page.start_edit_profile()
            page._type(page.name_input_locator, "This should not be saved")

        with allure.step("Cancel edit"):
            page.cancel_edit_profile()

        with allure.step("Verify name was not changed"):
            current_name = page.get_display_name()
            assert current_name == original_name, \
                "Display name changed after canceling edit"

    @allure.severity(allure.severity_level.CRITICAL)
    def test_change_password(self, authenticated_driver, test_user):
        """Test changing account password"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        old_password = test_user['password']
        new_password = "NewTestPassword123!"

        with allure.step("Change password"):
            page.change_password(old_password, new_password)

        with allure.step("Verify still on account page"):
            assert '/auth/account' in authenticated_driver.current_url, \
                "Unexpected redirect after password change"

        with allure.step("Change password back for cleanup"):
            page.change_password(new_password, old_password)

    @allure.severity(allure.severity_level.NORMAL)
    def test_change_password_wrong_old_password(self, authenticated_driver):
        """Test that changing password with wrong old password shows error"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        with allure.step("Attempt to change password with incorrect old password"):
            page._type(page.old_password_input_locator, "wrong_password")
            page._type(page.new_password_input_locator, "NewPassword123!")
            page._click(page.change_password_button_locator)

        with allure.step("Verify error message is displayed"):
            assert page.has_password_error(), \
                "Error message not displayed for incorrect old password"


@allure.feature('Account Management')
@allure.story('Account Deletion')
@pytest.mark.auth
class TestAccountDeletion:
    """Tests for account deletion through UI"""

    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_account_success(self, unauthenticated_driver, api_client):
        """Test successfully deleting an account through the UI"""
        # Create user via API
        rand_int = random.randint(0, 99999)
        username = f"test_delete_user{rand_int}"
        password = f"TestPass{rand_int}!"

        with allure.step("Create test user via API"):
            api_client.register_user(username, password)

        with allure.step("Login via UI"):
            login_page = LoginPage(unauthenticated_driver)
            login_page.login(username, password)

        with allure.step("Navigate to account page and delete account"):
            account_page = AccountPage(unauthenticated_driver)
            account_page.delete_account(password)

        with allure.step("Verify redirect to home page"):
            assert unauthenticated_driver.current_url == unauthenticated_driver.base_url + '/', \
                "User was not redirected to home page after account deletion"

        with allure.step("Verify user is logged out"):
            page = BaseAppPage(unauthenticated_driver)
            assert page.is_register_button_visible(), \
                "User appears to still be logged in after account deletion"


    @allure.severity(allure.severity_level.MINOR)
    def test_delete_account_cancel(self, authenticated_driver):
        """Test canceling account deletion"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        with allure.step("Start deletion and cancel"):
            page.cancel_delete()

        with allure.step("Verify still on account page"):
            assert '/auth/account' in authenticated_driver.current_url, \
                "Unexpected navigation after canceling account deletion"


    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_account_wrong_password(self, authenticated_driver):
        """Test that deleting account with wrong password shows error"""
        with allure.step("Navigate to account page"):
            page = AccountPage(authenticated_driver)

        with allure.step("Attempt to delete account with wrong password"):
            page._click(page.delete_button_locator)
            assert page._is_active(page.delete_password_input_locator, 3), \
                "Delete confirmation form did not appear"

            page._type(page.delete_password_input_locator, "wrong_password")
            page._click(page.confirm_delete_button_locator)

        with allure.step("Verify error message is displayed"):
            assert page.has_delete_error(), \
                "Error message not displayed for incorrect password during deletion"

        with allure.step("Verify still on account page (deletion failed)"):
            assert '/auth/account' in authenticated_driver.current_url, \
                "Unexpected navigation after failed deletion"