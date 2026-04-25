from pages.base_page import BasePage, locator_from_testid


class TaskSearchComponent(BasePage):
    """Component for interacting with the task search/filter interface.

    Has two states:
    - Simple (collapsed) - basic search box
    - Advanced (expanded) - full filter interface
    """

    def __init__(self, driver):
        super().__init__(driver)

    # ============================================================================
    # LOCATORS
    # ============================================================================

    def _component_locator(self):
        return locator_from_testid("task-search-component")

    def _simple_view_locator(self):
        """Simple search view - only available in COLLAPSED state"""
        return locator_from_testid("task-search-simple")

    def _advanced_view_locator(self):
        """Advanced search view - only available in EXPANDED state"""
        return locator_from_testid("task-search-advanced")

    # Simple view locators
    def _simple_input_locator(self):
        """Simple search input - only available in COLLAPSED state"""
        return locator_from_testid("task-search-simple-input")

    def _expand_button_locator(self):
        """Expand to advanced button - only available in COLLAPSED state"""
        return locator_from_testid("task-search-expand-button")

    def _simple_submit_button_locator(self):
        """Simple search submit button - only available in COLLAPSED state"""
        return locator_from_testid("task-search-simple-submit-button")

    def _active_filters_locator(self):
        """Active filters display - only available in COLLAPSED state"""
        return locator_from_testid("task-search-active-filters")

    def _clear_filters_tag_locator(self):
        """Clear filters tag button - only available in COLLAPSED state"""
        return locator_from_testid("task-search-clear-filters-tag")

    # Advanced view locators
    def _collapse_button_locator(self):
        """Collapse to simple button - only available in EXPANDED state"""
        return locator_from_testid("task-search-collapse-button")

    def _title_input_locator(self):
        """Title search input - only available in EXPANDED state"""
        return locator_from_testid("task-search-title-input")

    def _description_input_locator(self):
        """Description search input - only available in EXPANDED state"""
        return locator_from_testid("task-search-description-input")

    # Status checkboxes (EXPANDED state only)
    def _status_open_checkbox_locator(self):
        return locator_from_testid("task-search-status-open-checkbox")

    def _status_waiting_checkbox_locator(self):
        return locator_from_testid("task-search-status-waiting-checkbox")

    def _status_deferred_checkbox_locator(self):
        return locator_from_testid("task-search-status-deferred-checkbox")

    def _status_declined_checkbox_locator(self):
        return locator_from_testid("task-search-status-declined-checkbox")

    def _status_stale_checkbox_locator(self):
        return locator_from_testid("task-search-status-stale-checkbox")

    # Active status radios (EXPANDED state only)
    def _active_status_active_radio_locator(self):
        return locator_from_testid("task-search-active-status-active-radio")

    def _active_status_all_radio_locator(self):
        return locator_from_testid("task-search-active-status-all-radio")

    def _active_status_inactive_radio_locator(self):
        return locator_from_testid("task-search-active-status-inactive-radio")

    # Completion status radios (EXPANDED state only)
    def _completion_status_incomplete_radio_locator(self):
        return locator_from_testid("task-search-completion-status-incomplete-radio")

    def _completion_status_all_radio_locator(self):
        return locator_from_testid("task-search-completion-status-all-radio")

    def _completion_status_complete_radio_locator(self):
        return locator_from_testid("task-search-completion-status-complete-radio")

    # Action buttons (EXPANDED state only)
    def _clear_filters_button_locator(self):
        """Clear filters button - only available in EXPANDED state"""
        return locator_from_testid("task-search-clear-filters-button")

    def _apply_filters_button_locator(self):
        """Apply filters button - only available in EXPANDED state"""
        return locator_from_testid("task-search-apply-filters-button")

    # ============================================================================
    # STATE CHECKING
    # ============================================================================

    def is_collapsed(self, timeout=2):
        """Check if search is in collapsed/simple state"""
        return self._is_displayed(self._simple_view_locator(), timeout=timeout)

    def is_expanded(self, timeout=2):
        """Check if search is in expanded/advanced state"""
        return self._is_displayed(self._advanced_view_locator(), timeout=timeout)

    def _ensure_collapsed(self):
        """Ensure search is in collapsed state, raise error if not"""
        if not self.is_collapsed(timeout=1):
            raise AssertionError(
                "TaskSearch must be in COLLAPSED state for this operation. "
                f"Current state: {'EXPANDED' if self.is_expanded(timeout=0) else 'UNKNOWN'}"
            )

    def _ensure_expanded(self):
        """Ensure search is in expanded state, raise error if not"""
        if not self.is_expanded(timeout=1):
            raise AssertionError(
                "TaskSearch must be in EXPANDED state for this operation. "
                f"Current state: {'COLLAPSED' if self.is_collapsed(timeout=0) else 'UNKNOWN'}"
            )

    # ============================================================================
    # STATE TRANSITIONS
    # ============================================================================

    def expand(self):
        """Expand to advanced search view"""
        if self.is_expanded():
            return  # Already expanded

        self._click(self._expand_button_locator())
        assert self._is_active(self._advanced_view_locator(), 3), \
            "Search component did not expand to advanced view"

    def collapse(self):
        """Collapse to simple search view"""
        if self.is_collapsed():
            return  # Already collapsed

        self._click(self._collapse_button_locator())
        assert self._is_active(self._simple_view_locator(), 3), \
            "Search component did not collapse to simple view"

    # ============================================================================
    # SIMPLE SEARCH ACTIONS
    # ============================================================================

    def simple_search(self, query):
        """Perform a simple search.

        Ensures component is collapsed, enters query, and submits.

        Args:
            query: Search query string
        """
        if not self.is_collapsed():
            self.collapse()

        self._type(self._simple_input_locator(), query)
        self._click(self._simple_submit_button_locator())

    def get_simple_search_value(self):
        """Get the current value in the simple search input.

        Requires component to be in collapsed state.
        """
        self._ensure_collapsed()
        element = self._find(self._simple_input_locator())
        return element.get_attribute('value')

    # ============================================================================
    # ADVANCED SEARCH ACTIONS
    # ============================================================================

    def set_title_filter(self, title):
        """Set the title filter in advanced search.

        Ensures component is expanded first.

        Args:
            title: Title search string
        """
        if not self.is_expanded():
            self.expand()

        self._type(self._title_input_locator(), title)

    def set_description_filter(self, description):
        """Set the description filter in advanced search.

        Ensures component is expanded first.

        Args:
            description: Description search string
        """
        if not self.is_expanded():
            self.expand()

        self._type(self._description_input_locator(), description)

    def set_status_filters(self, *statuses):
        """Set status checkboxes in advanced search.

        Ensures component is expanded first.

        Args:
            *statuses: Variable number of status strings
                      (e.g., 'open', 'waiting', 'deferred', 'declined', 'stale')
        """
        if not self.is_expanded():
            self.expand()

        status_locators = {
            'open': self._status_open_checkbox_locator(),
            'waiting': self._status_waiting_checkbox_locator(),
            'deferred': self._status_deferred_checkbox_locator(),
            'declined': self._status_declined_checkbox_locator(),
            'stale': self._status_stale_checkbox_locator(),
        }

        for status in statuses:
            if status in status_locators:
                self._click(status_locators[status])

    def set_active_status_filter(self, active_status):
        """Set the active status filter in advanced search.

        Ensures component is expanded first.

        Args:
            active_status: One of 'active', 'all', 'inactive'
        """
        if not self.is_expanded():
            self.expand()

        active_radios = {
            'active': self._active_status_active_radio_locator(),
            'all': self._active_status_all_radio_locator(),
            'inactive': self._active_status_inactive_radio_locator(),
        }

        if active_status in active_radios:
            self._click(active_radios[active_status])
        else:
            raise ValueError(f"Invalid active_status: {active_status}. Must be 'active', 'all', or 'inactive'")

    def set_completion_status_filter(self, completion_status):
        """Set the completion status filter in advanced search.

        Ensures component is expanded first.

        Args:
            completion_status: One of 'incomplete', 'all', 'complete'
        """
        if not self.is_expanded():
            self.expand()

        completion_radios = {
            'incomplete': self._completion_status_incomplete_radio_locator(),
            'all': self._completion_status_all_radio_locator(),
            'complete': self._completion_status_complete_radio_locator(),
        }

        if completion_status in completion_radios:
            self._click(completion_radios[completion_status])
        else:
            raise ValueError(
                f"Invalid completion_status: {completion_status}. Must be 'incomplete', 'all', or 'complete'")

    def apply_filters(self):
        """Apply the current filters and submit search.

        Requires component to be in expanded state.
        """
        self._ensure_expanded()
        self._click(self._apply_filters_button_locator())

    def clear_filters(self):
        """Clear all filters.

        Works from either collapsed or expanded state.
        """
        if self.is_collapsed():
            # Use the tag button in collapsed state (if visible)
            if self._is_displayed(self._clear_filters_tag_locator(), timeout=1):
                self._click(self._clear_filters_tag_locator())
        else:
            # Use the button in expanded state
            self._click(self._clear_filters_button_locator())

    # ============================================================================
    # HIGH-LEVEL ACTIONS
    # ============================================================================

    def advanced_search(self, title=None, description=None, statuses=None,
                        active_status="all", completion_status="incomplete"):
        """Perform an advanced search with multiple filters.

        This is a convenience method that:
        1. Expands to advanced view
        2. Sets all specified filters
        3. Applies the filters

        Args:
            title: Title search string (optional)
            description: Description search string (optional)
            statuses: List/tuple of status strings to filter (optional)
            active_status: 'active', 'all', or 'inactive' (default: 'all')
            completion_status: 'incomplete', 'all', or 'complete' (default: 'incomplete')
        """
        # Expand if needed
        if not self.is_expanded():
            self.expand()

        # Set filters
        if title:
            self.set_title_filter(title)

        if description:
            self.set_description_filter(description)

        if statuses:
            self.set_status_filters(*statuses)

        if active_status != "all":
            self.set_active_status_filter(active_status)

        if completion_status != "incomplete":
            self.set_completion_status_filter(completion_status)

        # Apply
        self.apply_filters()

    # ============================================================================
    # VERIFICATION HELPERS
    # ============================================================================

    def has_active_filters(self):
        """Check if the active filters indicator is displayed.

        Requires component to be in collapsed state.

        Returns:
            bool: True if active filters indicator is shown
        """
        self._ensure_collapsed()
        return self._is_displayed(self._active_filters_locator(), timeout=1)