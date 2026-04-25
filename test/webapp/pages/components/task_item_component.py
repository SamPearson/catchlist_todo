from pages.base_page import BasePage, locator_from_testid
from selenium.webdriver.support.ui import Select


class TaskItemComponent(BasePage):
    """Component for interacting with a task item in any of its three states:
    - Minimized (collapsed)
    - Expanded (view mode)
    - Edit mode
    """
    
    def __init__(self, driver, task_id):
        super().__init__(driver)
        self.task_id = task_id
    
    # ============================================================================
    # LOCATORS
    # ============================================================================
    
    def _minimized_locator(self):
        return locator_from_testid(f"task-item-{self.task_id}-minimized")
    
    def _expanded_locator(self):
        return locator_from_testid(f"task-item-{self.task_id}-expanded")
    
    def _edit_form_locator(self):
        return locator_from_testid(f"task-edit-{self.task_id}-form")
    
    # Minimized view locators
    def _title_locator(self):
        """Title element - only available in MINIMIZED state"""
        return locator_from_testid(f"task-item-{self.task_id}-title")
    
    # Expanded view locators
    def _collapse_button_locator(self):
        """Collapse button - only available in EXPANDED state"""
        return locator_from_testid(f"task-item-{self.task_id}-collapse-button")
    
    def _status_badge_locator(self):
        """Status badge - only available in EXPANDED state"""
        return locator_from_testid(f"task-item-{self.task_id}-status-badge")
    
    def _description_locator(self):
        """Description - only available in EXPANDED state"""
        return locator_from_testid(f"task-item-{self.task_id}-description")
    
    def _edit_button_locator(self):
        """Edit button - only available in EXPANDED VIEW mode"""
        return locator_from_testid(f"task-item-{self.task_id}-edit-button")
    
    def _delete_button_locator(self):
        """Delete button - available in EXPANDED state"""
        return locator_from_testid(f"task-item-{self.task_id}-delete-button")
    
    def _complete_button_locator(self):
        """Complete button - available in EXPANDED state (active tasks)"""
        return locator_from_testid(f"task-item-{self.task_id}-complete-button")
    
    def _uncomplete_button_locator(self):
        """Uncomplete button - available in EXPANDED state (completed tasks)"""
        return locator_from_testid(f"task-item-{self.task_id}-uncomplete-button")
    
    def _activate_button_locator(self):
        """Activate button - available in EXPANDED state (inactive tasks)"""
        return locator_from_testid(f"task-item-{self.task_id}-activate-button")
    
    def _completed_badge_locator(self):
        """Completed badge - available in EXPANDED state"""
        return locator_from_testid(f"task-item-{self.task_id}-completed-badge")
    
    # Edit mode locators
    def _edit_title_input_locator(self):
        """Title input - only available in EDIT mode"""
        return locator_from_testid(f"task-edit-{self.task_id}-title-input")
    
    def _edit_description_input_locator(self):
        """Description input - only available in EDIT mode"""
        return locator_from_testid(f"task-edit-{self.task_id}-description-input")
    
    def _edit_status_select_locator(self):
        """Status select - only available in EDIT mode"""
        return locator_from_testid(f"task-edit-{self.task_id}-status-select")
    
    def _edit_active_checkbox_locator(self):
        """Active checkbox - only available in EDIT mode"""
        return locator_from_testid(f"task-edit-{self.task_id}-active-checkbox")
    
    def _edit_save_button_locator(self):
        """Save button - only available in EDIT mode"""
        return locator_from_testid(f"task-edit-{self.task_id}-save-button")
    
    def _edit_cancel_button_locator(self):
        """Cancel button - only available in EDIT mode"""
        return locator_from_testid(f"task-edit-{self.task_id}-cancel-button")
    
    def _edit_title_error_locator(self):
        """Title error - only available in EDIT mode"""
        return locator_from_testid(f"task-edit-{self.task_id}-title-error")
    
    # ============================================================================
    # STATE CHECKING
    # ============================================================================
    
    def is_minimized(self, timeout=2):
        """Check if task is in minimized state"""
        return self._is_displayed(self._minimized_locator(), timeout=timeout)
    
    def is_expanded(self, timeout=2):
        """Check if task is in expanded state"""
        return self._is_displayed(self._expanded_locator(), timeout=timeout)
    
    def is_in_edit_mode(self, timeout=2):
        """Check if task is in edit mode"""
        return self._is_displayed(self._edit_form_locator(), timeout=timeout)
    
    def is_in_view_mode(self, timeout=2):
        """Check if task is in view mode (expanded but not editing)"""
        return (self._is_displayed(self._expanded_locator(), timeout=timeout) and
                self._is_displayed(self._edit_button_locator(), timeout=timeout))
    
    def _ensure_minimized(self):
        """Ensure task is in minimized state, raise error if not"""
        if not self.is_minimized(timeout=1):
            raise AssertionError(
                f"Task {self.task_id} must be in MINIMIZED state for this operation. "
                f"Current state: {'EXPANDED' if self.is_expanded(timeout=0) else 'EDIT' if self.is_in_edit_mode(timeout=0) else 'UNKNOWN'}"
            )
    
    def _ensure_expanded(self):
        """Ensure task is in expanded state, raise error if not"""
        if not self.is_expanded(timeout=1):
            raise AssertionError(
                f"Task {self.task_id} must be in EXPANDED state for this operation. "
                f"Current state: {'MINIMIZED' if self.is_minimized(timeout=0) else 'EDIT' if self.is_in_edit_mode(timeout=0) else 'UNKNOWN'}"
            )
    
    def _ensure_edit_mode(self):
        """Ensure task is in edit mode, raise error if not"""
        if not self.is_in_edit_mode(timeout=1):
            raise AssertionError(
                f"Task {self.task_id} must be in EDIT mode for this operation. "
                f"Current state: {'MINIMIZED' if self.is_minimized(timeout=0) else 'EXPANDED' if self.is_expanded(timeout=0) else 'UNKNOWN'}"
            )
    
    # ============================================================================
    # STATE TRANSITIONS
    # ============================================================================
    
    def expand(self):
        """Expand the task to show details"""
        if self.is_expanded():
            return  # Already expanded
        
        self._click(self._minimized_locator())
        assert self._is_active(self._expanded_locator(), 3), \
            f"Task {self.task_id} did not expand"
    
    def collapse(self):
        """Collapse the task back to minimized view"""
        if self.is_minimized():
            return  # Already minimized
        
        self._click(self._collapse_button_locator())
        assert self._is_active(self._minimized_locator(), 3), \
            f"Task {self.task_id} did not collapse"
    
    def enter_edit_mode(self):
        """Enter edit mode for this task"""
        # Ensure we're expanded first
        if not self.is_expanded():
            self.expand()
        
        # Click edit button
        self._click(self._edit_button_locator())
        assert self._is_active(self._edit_form_locator(), 3), \
            f"Task {self.task_id} did not enter edit mode"
    
    def cancel_edit(self):
        """Cancel editing and return to view mode"""
        self._ensure_edit_mode()
        self._click(self._edit_cancel_button_locator())
        assert self.is_in_view_mode(timeout=3), \
            f"Task {self.task_id} did not return to view mode after cancel"
    
    # ============================================================================
    # DATA RETRIEVAL
    # ============================================================================
    
    def get_title_from_minimized(self):
        """Get the task title text from minimized view.
        
        Requires task to be in minimized state.
        """
        self._ensure_minimized()
        element = self._find(self._title_locator())
        return element.text
    
    def get_status_from_expanded(self):
        """Get the task status from expanded view.
        
        Requires task to be in expanded state.
        Returns the status as a lowercase string (e.g., 'open', 'deferred').
        """
        self._ensure_expanded()
        
        if self._is_displayed(self._status_badge_locator(), timeout=1):
            status_element = self._find(self._status_badge_locator())
            return status_element.text.lower()
        return None
    
    def get_description_from_expanded(self):
        """Get the task description from expanded view.
        
        Requires task to be in expanded state.
        Returns description text or None if no description.
        """
        self._ensure_expanded()
        
        if self._is_displayed(self._description_locator(), timeout=1):
            desc_element = self._find(self._description_locator())
            return desc_element.text
        return None
    
    def is_completed(self):
        """Check if task is completed.
        
        Requires task to be in expanded state.
        """
        self._ensure_expanded()
        return self._is_displayed(self._completed_badge_locator(), timeout=1)
    
    def is_active(self):
        """Check if task is active (not someday/maybe).
        
        Requires task to be in expanded state.
        Returns True if active, False if someday/maybe.
        """
        self._ensure_expanded()
        # If activate button is present, task is inactive
        return not self._is_displayed(self._activate_button_locator(), timeout=1)
    
    def get_details(self):
        """Get task details from current state.
        
        This is a convenience method that:
        1. Gets title from minimized state (if minimized)
        2. Expands task if needed
        3. Gathers all available details from expanded state
        4. Returns a dict with all details
        
        Returns dict with fields: title, status, description, is_completed, is_active
        """
        # Get title while minimized (if we're minimized)
        if self.is_minimized():
            title = self.get_title_from_minimized()
        else:
            title = None
        
        # Ensure expanded to get other details
        if not self.is_expanded():
            self.expand()
        
        details = {
            'status': self.get_status_from_expanded(),
            'description': self.get_description_from_expanded(),
            'is_completed': self.is_completed(),
            'is_active': self.is_active()
        }
        
        # If we got title earlier, use it; otherwise we need to collapse to get it
        if title:
            details['title'] = title
        else:
            # We're expanded, need to collapse to read title
            self.collapse()
            details['title'] = self.get_title_from_minimized()
            # Re-expand for consistency
            self.expand()
        
        return details
    
    # ============================================================================
    # HIGH-LEVEL ACTIONS
    # ============================================================================
    
    def edit_and_save(self, title=None, description=None, status=None, active=None):
        """High-level action: Enter edit mode, make changes, and save.
        
        Args:
            title: New title (optional)
            description: New description (optional)
            status: New status value (optional)
            active: New active status boolean (optional)
        """
        self.enter_edit_mode()
        
        # Make changes
        if title is not None:
            title_input = self._find(self._edit_title_input_locator())
            title_input.clear()
            self._type(self._edit_title_input_locator(), title)
        
        if description is not None:
            desc_input = self._find(self._edit_description_input_locator())
            desc_input.clear()
            self._type(self._edit_description_input_locator(), description)
        
        if status is not None:
            select_element = self._find(self._edit_status_select_locator())
            select = Select(select_element)
            select.select_by_value(status)
        
        if active is not None:
            checkbox = self._find(self._edit_active_checkbox_locator())
            is_checked = checkbox.is_selected()
            if active and not is_checked:
                self._click(self._edit_active_checkbox_locator())
            elif not active and is_checked:
                self._click(self._edit_active_checkbox_locator())
        
        # Save
        self._click(self._edit_save_button_locator())
        assert self.is_in_view_mode(timeout=3), \
            f"Task {self.task_id} did not return to view mode after save"
    
    def delete(self):
        """Delete the task (handles confirmation dialog)"""
        # Ensure we're expanded
        if not self.is_expanded():
            self.expand()
        
        self._click(self._delete_button_locator())
        # Note: Caller needs to handle the browser alert
    
    def complete(self):
        """Mark task as complete"""
        if not self.is_expanded():
            self.expand()
        
        self._click(self._complete_button_locator())
    
    def uncomplete(self):
        """Mark task as incomplete"""
        if not self.is_expanded():
            self.expand()
        
        self._click(self._uncomplete_button_locator())
    
    def activate(self):
        """Activate a someday/maybe task"""
        if not self.is_expanded():
            self.expand()
        
        self._click(self._activate_button_locator())
    
    # ============================================================================
    # VERIFICATION HELPERS
    # ============================================================================
    
    def verify_status(self, expected_status):
        """Verify the task has the expected status.
        
        Ensures task is expanded, then checks status.
        
        Args:
            expected_status: Expected status string (e.g., 'open', 'deferred')
        
        Returns:
            bool: True if status matches, False otherwise
        """
        if not self.is_expanded():
            self.expand()
        
        actual_status = self.get_status_from_expanded()
        return actual_status == expected_status.lower()
    
    def verify_title(self, expected_title):
        """Verify the task has the expected title.
        
        Ensures task is minimized, then checks title.
        
        Args:
            expected_title: Expected title string
        
        Returns:
            bool: True if title matches, False otherwise
        """
        if not self.is_minimized():
            self.collapse()
        
        actual_title = self.get_title_from_minimized()
        return actual_title == expected_title
    
    def has_edit_error(self, field='title'):
        """Check if an edit form validation error is displayed.
        
        Requires task to be in edit mode.
        
        Args:
            field: Which field to check for errors (default: 'title')
        
        Returns:
            bool: True if error is displayed
        """
        self._ensure_edit_mode()
        
        if field == 'title':
            return self._is_displayed(self._edit_title_error_locator(), timeout=2)
        # Add other fields as needed
        return False