from pages.base_page import BasePage, locator_from_testid
from selenium.webdriver.support.ui import Select


class TaskCreateComponent(BasePage):
    """Component for interacting with the task creation form.

    This component has a single state - the form is always displayed.
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ============================================================================
    # LOCATORS
    # ============================================================================

    def _form_locator(self):
        """Main form container"""
        return locator_from_testid("task-create-form")

    def _title_input_locator(self):
        """Title input field"""
        return locator_from_testid("task-create-title-input")

    def _description_input_locator(self):
        """Description textarea field"""
        return locator_from_testid("task-create-description-input")

    def _status_select_locator(self):
        """Status dropdown select"""
        return locator_from_testid("task-create-status-select")

    def _active_checkbox_locator(self):
        """Active checkbox"""
        return locator_from_testid("task-create-active-checkbox")

    def _cancel_button_locator(self):
        """Cancel button"""
        return locator_from_testid("task-create-cancel-button")

    def _submit_button_locator(self):
        """Submit/Create button"""
        return locator_from_testid("task-create-submit-button")

    def _title_error_locator(self):
        """Title validation error message"""
        return locator_from_testid("task-create-title-error")

    # ============================================================================
    # FORM FIELD INTERACTIONS
    # ============================================================================

    def set_title(self, title):
        """Set the task title.

        Args:
            title: Title string
        """
        self._type(self._title_input_locator(), title)

    def set_description(self, description):
        """Set the task description.

        Args:
            description: Description string
        """
        self._type(self._description_input_locator(), description)

    def set_status(self, status):
        """Set the task status.

        Args:
            status: Status value (e.g., 'open', 'waiting', 'deferred', 'declined', 'stale')
        """
        valid_statuses = ['open', 'waiting', 'deferred', 'declined', 'stale']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        select_element = self._find(self._status_select_locator())
        select = Select(select_element)
        select.select_by_value(status)

    def set_active(self, active):
        """Set the active checkbox state.

        Args:
            active: Boolean - True for active, False for someday/maybe
        """
        checkbox = self._find(self._active_checkbox_locator())
        is_checked = checkbox.is_selected()

        # Only click if we need to change the state
        if active and not is_checked:
            self._click(self._active_checkbox_locator())
        elif not active and is_checked:
            self._click(self._active_checkbox_locator())

    def get_title_value(self):
        """Get the current value in the title input.

        Returns:
            str: Current title value
        """
        element = self._find(self._title_input_locator())
        return element.get_attribute('value')

    def get_description_value(self):
        """Get the current value in the description textarea.

        Returns:
            str: Current description value
        """
        element = self._find(self._description_input_locator())
        return element.get_attribute('value')

    def get_status_value(self):
        """Get the currently selected status.

        Returns:
            str: Current status value
        """
        select_element = self._find(self._status_select_locator())
        select = Select(select_element)
        return select.first_selected_option.get_attribute('value')

    def is_active_checked(self):
        """Check if the active checkbox is checked.

        Returns:
            bool: True if checked, False otherwise
        """
        checkbox = self._find(self._active_checkbox_locator())
        return checkbox.is_selected()

    # ============================================================================
    # FORM ACTIONS
    # ============================================================================

    def submit(self):
        """Click the submit/create button"""
        self._click(self._submit_button_locator())

    def cancel(self):
        """Click the cancel button"""
        self._click(self._cancel_button_locator())

    def clear_form(self):
        """Clear all form fields back to defaults.

        This simulates what the cancel button does - resets to initial state.
        """
        # Clear text fields
        title_input = self._find(self._title_input_locator())
        title_input.clear()

        desc_input = self._find(self._description_input_locator())
        desc_input.clear()

        # Reset status to 'open'
        if self.get_status_value() != 'open':
            self.set_status('open')

        # Ensure active is checked (default state)
        if not self.is_active_checked():
            self.set_active(True)

    # ============================================================================
    # HIGH-LEVEL ACTIONS
    # ============================================================================

    def create_task(self, title, description=None, status='open', active=True):
        """Create a task by filling out the form and submitting.

        This is a convenience method that fills all fields and submits in one call.

        Args:
            title: Task title (required)
            description: Task description (optional)
            status: Task status (default: 'open')
            active: Active checkbox state (default: True)
        """
        # Fill in title
        self.set_title(title)

        # Fill in description if provided
        if description:
            self.set_description(description)

        # Set status if not default
        if status != 'open':
            self.set_status(status)

        # Set active checkbox
        self.set_active(active)

        # Submit
        self.submit()

    # ============================================================================
    # VALIDATION & ERROR CHECKING
    # ============================================================================

    def has_title_error(self):
        """Check if a title validation error is displayed.

        Returns:
            bool: True if error is displayed
        """
        return self._is_displayed(self._title_error_locator(), timeout=2)

    def get_title_error_text(self):
        """Get the title validation error message text.

        Returns:
            str: Error message text, or None if no error displayed
        """
        if not self.has_title_error():
            return None

        element = self._find(self._title_error_locator())
        return element.text

    def is_form_displayed(self):
        """Check if the create form is displayed.

        Returns:
            bool: True if form is visible
        """
        return self._is_displayed(self._form_locator(), timeout=2)

    # ============================================================================
    # VERIFICATION HELPERS
    # ============================================================================

    def verify_form_cleared(self):
        """Verify that the form has been cleared to defaults.

        Returns:
            bool: True if form is in default state
        """
        return (
                self.get_title_value() == '' and
                self.get_description_value() == '' and
                self.get_status_value() == 'open' and
                self.is_active_checked()
        )