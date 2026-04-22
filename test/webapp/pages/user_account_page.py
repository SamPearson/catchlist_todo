from pages.base_app_page import BaseAppPage
from pages.base_page import locator_from_testid


class AccountPage(BaseAppPage):
    # Profile display elements
    username_display_locator = locator_from_testid("account-username-display")
    displayname_display_locator = locator_from_testid("account-displayname-display")
    timezone_display_locator = locator_from_testid("account-timezone-display")
    created_display_locator = locator_from_testid("account-created-display")

    # Profile edit buttons
    edit_profile_button_locator = locator_from_testid("account-edit-profile-button")
    save_profile_button_locator = locator_from_testid("account-save-profile-button")
    cancel_profile_button_locator = locator_from_testid("account-cancel-profile-button")

    # Profile edit inputs
    name_input_locator = locator_from_testid("account-name-input")
    timezone_select_locator = locator_from_testid("account-timezone-select")

    # Profile messages
    profile_error_message_locator = locator_from_testid("account-profile-error-message")
    profile_success_message_locator = locator_from_testid("account-profile-success-message")

    # Change password elements
    old_password_input_locator = locator_from_testid("account-old-password-input")
    new_password_input_locator = locator_from_testid("account-new-password-input")
    change_password_button_locator = locator_from_testid("account-change-password-button")
    password_error_message_locator = locator_from_testid("account-password-error-message")
    password_success_message_locator = locator_from_testid("account-password-success-message")

    # Delete account elements
    delete_button_locator = locator_from_testid("account-delete-button")
    delete_password_input_locator = locator_from_testid("account-delete-password-input")
    confirm_delete_button_locator = locator_from_testid("account-confirm-delete-button")
    cancel_delete_button_locator = locator_from_testid("account-cancel-delete-button")
    delete_error_message_locator = locator_from_testid("account-delete-error-message")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/auth/account")

    def get_username(self):
        """Get the displayed username"""
        element = self._find(self.username_display_locator)
        return element.text

    def get_display_name(self):
        """Get the displayed name"""
        element = self._find(self.displayname_display_locator)
        return element.text

    def get_timezone(self):
        """Get the displayed timezone"""
        element = self._find(self.timezone_display_locator)
        return element.text

    def start_edit_profile(self):
        """Click the edit profile button"""
        self._click(self.edit_profile_button_locator)
        # Wait for the form to appear
        assert self._is_active(self.name_input_locator, 3), "Profile edit form did not appear"

    def update_profile(self, name=None, timezone=None):
        """Update profile information"""
        self.start_edit_profile()

        if name is not None:
            self._type(self.name_input_locator, name)

        if timezone is not None:
            # For select elements, we need to use a different approach
            from selenium.webdriver.support.ui import Select
            select_element = self._find(self.timezone_select_locator)
            select = Select(select_element)
            select.select_by_value(timezone)

        self._click(self.save_profile_button_locator)

        # Wait for success message
        assert self._is_active(self.profile_success_message_locator, 5), "Profile update success message not shown"

    def cancel_edit_profile(self):
        """Cancel profile editing"""
        self._click(self.cancel_profile_button_locator)

    def change_password(self, old_password, new_password):
        """Change account password"""
        self._type(self.old_password_input_locator, old_password)
        self._type(self.new_password_input_locator, new_password)
        self._click(self.change_password_button_locator)

        # Wait for success message
        assert self._is_active(self.password_success_message_locator, 5), "Password change success message not shown"

    def delete_account(self, password):
        """Delete the account"""
        self._click(self.delete_button_locator)

        # Wait for confirmation form to appear
        assert self._is_active(self.delete_password_input_locator, 3), "Delete confirmation form did not appear"

        self._type(self.delete_password_input_locator, password)
        self._click(self.confirm_delete_button_locator)

        # Wait for redirect to home page
        self._wait_for_url('is', self.driver.base_url + '/', timeout=10)

    def cancel_delete(self):
        """Cancel account deletion"""
        self._click(self.delete_button_locator)
        assert self._is_active(self.cancel_delete_button_locator, 3), "Delete confirmation form did not appear"
        self._click(self.cancel_delete_button_locator)

    def has_profile_error(self):
        """Check if profile error message is displayed"""
        return self._is_displayed(self.profile_error_message_locator, timeout=2)

    def has_password_error(self):
        """Check if password error message is displayed"""
        return self._is_displayed(self.password_error_message_locator, timeout=2)

    def has_delete_error(self):
        """Check if delete error message is displayed"""
        return self._is_displayed(self.delete_error_message_locator, timeout=2)