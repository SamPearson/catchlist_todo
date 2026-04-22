from pages.base_app_page import BaseAppPage
from pages.base_page import locator_from_testid


class TaskComponentDemoPage(BaseAppPage):
    # Page sections
    search_section_locator = locator_from_testid("demo-search-section")
    create_section_locator = locator_from_testid("demo-create-section")
    tasks_section_locator = locator_from_testid("demo-tasks-section")

    # Task Create Form
    create_title_input_locator = locator_from_testid("task-create-title-input")
    create_description_input_locator = locator_from_testid("task-create-description-input")
    create_status_select_locator = locator_from_testid("task-create-status-select")
    create_active_checkbox_locator = locator_from_testid("task-create-active-checkbox")
    create_cancel_button_locator = locator_from_testid("task-create-cancel-button")
    create_submit_button_locator = locator_from_testid("task-create-submit-button")
    create_title_error_locator = locator_from_testid("task-create-title-error")

    # Task created notification
    task_created_notification_locator = locator_from_testid("demo-task-created-notification")
    reset_create_button_locator = locator_from_testid("demo-reset-create-button")

    # Task Search - Simple
    search_simple_input_locator = locator_from_testid("task-search-simple-input")
    search_expand_button_locator = locator_from_testid("task-search-expand-button")
    search_simple_submit_button_locator = locator_from_testid("task-search-simple-submit-button")
    search_active_filters_locator = locator_from_testid("task-search-active-filters")
    search_clear_filters_tag_locator = locator_from_testid("task-search-clear-filters-tag")

    # Task Search - Advanced
    search_advanced_locator = locator_from_testid("task-search-advanced")
    search_collapse_button_locator = locator_from_testid("task-search-collapse-button")
    search_title_input_locator = locator_from_testid("task-search-title-input")
    search_description_input_locator = locator_from_testid("task-search-description-input")

    # Task Search - Status checkboxes
    search_status_open_checkbox_locator = locator_from_testid("task-search-status-open-checkbox")
    search_status_waiting_checkbox_locator = locator_from_testid("task-search-status-waiting-checkbox")
    search_status_deferred_checkbox_locator = locator_from_testid("task-search-status-deferred-checkbox")
    search_status_declined_checkbox_locator = locator_from_testid("task-search-status-declined-checkbox")
    search_status_stale_checkbox_locator = locator_from_testid("task-search-status-stale-checkbox")

    # Task Search - Active status radios
    search_active_status_active_radio_locator = locator_from_testid("task-search-active-status-active-radio")
    search_active_status_all_radio_locator = locator_from_testid("task-search-active-status-all-radio")
    search_active_status_inactive_radio_locator = locator_from_testid("task-search-active-status-inactive-radio")

    # Task Search - Completion status radios
    search_completion_status_incomplete_radio_locator = locator_from_testid("task-search-completion-status-incomplete-radio")
    search_completion_status_all_radio_locator = locator_from_testid("task-search-completion-status-all-radio")
    search_completion_status_complete_radio_locator = locator_from_testid("task-search-completion-status-complete-radio")

    # Task Search - Action buttons
    search_clear_filters_button_locator = locator_from_testid("task-search-clear-filters-button")
    search_apply_filters_button_locator = locator_from_testid("task-search-apply-filters-button")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/component-demo/tasks")

    # Task Creation Methods
    def create_task(self, title, description=None, status="open", active=True):
        """Create a new task using the create form"""
        self._type(self.create_title_input_locator, title)

        if description:
            self._type(self.create_description_input_locator, description)

        if status != "open":
            from selenium.webdriver.support.ui import Select
            select_element = self._find(self.create_status_select_locator)
            select = Select(select_element)
            select.select_by_value(status)

        # Handle active checkbox (it's checked by default)
        checkbox = self._find(self.create_active_checkbox_locator)
        is_checked = checkbox.is_selected()
        if active and not is_checked:
            self._click(self.create_active_checkbox_locator)
        elif not active and is_checked:
            self._click(self.create_active_checkbox_locator)

        self._click(self.create_submit_button_locator)

        # Wait for success notification
        assert self._is_active(self.task_created_notification_locator, 5), "Task creation notification not shown"

    def cancel_task_creation(self):
        """Cancel creating a task"""
        self._click(self.create_cancel_button_locator)

    def reset_create_form(self):
        """Reset the create form to create another task"""
        self._click(self.reset_create_button_locator)

    def has_create_title_error(self):
        """Check if title validation error is displayed"""
        return self._is_displayed(self.create_title_error_locator, timeout=2)

    # Task Search Methods
    def simple_search(self, query):
        """Perform a simple search"""
        self._type(self.search_simple_input_locator, query)
        self._click(self.search_simple_submit_button_locator)

    def expand_advanced_search(self):
        """Expand to advanced search view"""
        self._click(self.search_expand_button_locator)
        assert self._is_active(self.search_advanced_locator, 3), "Advanced search form did not appear"

    def collapse_advanced_search(self):
        """Collapse back to simple search"""
        self._click(self.search_collapse_button_locator)

    def advanced_search(self, title=None, description=None, statuses=None,
                        active_status="all", completion_status="incomplete"):
        """Perform an advanced search with filters"""
        self.expand_advanced_search()

        if title:
            self._type(self.search_title_input_locator, title)

        if description:
            self._type(self.search_description_input_locator, description)

        if statuses:
            status_checkboxes = {
                'open': self.search_status_open_checkbox_locator,
                'waiting': self.search_status_waiting_checkbox_locator,
                'deferred': self.search_status_deferred_checkbox_locator,
                'declined': self.search_status_declined_checkbox_locator,
                'stale': self.search_status_stale_checkbox_locator,
            }
            for status in statuses:
                if status in status_checkboxes:
                    self._click(status_checkboxes[status])

        # Set active status radio
        active_radios = {
            'active': self.search_active_status_active_radio_locator,
            'all': self.search_active_status_all_radio_locator,
            'inactive': self.search_active_status_inactive_radio_locator,
        }
        if active_status in active_radios:
            self._click(active_radios[active_status])

        # Set completion status radio
        completion_radios = {
            'incomplete': self.search_completion_status_incomplete_radio_locator,
            'all': self.search_completion_status_all_radio_locator,
            'complete': self.search_completion_status_complete_radio_locator,
        }
        if completion_status in completion_radios:
            self._click(completion_radios[completion_status])

        self._click(self.search_apply_filters_button_locator)

    def clear_search_filters(self):
        """Clear all search filters"""
        if self._is_displayed(self.search_advanced_locator):
            self._click(self.search_clear_filters_button_locator)
        else:
            self._click(self.search_clear_filters_tag_locator)

    # Task Item Methods (for interacting with the demo tasks)
    def get_task_item_locator(self, task_id, state="minimized"):
        """Get locator for a specific task item"""
        return locator_from_testid(f"task-item-{task_id}-{state}")

    def expand_task(self, task_id):
        """Click a task to expand it"""
        locator = locator_from_testid(f"task-item-{task_id}-minimized")
        self._click(locator)
        # Wait for expanded view
        expanded_locator = locator_from_testid(f"task-item-{task_id}-expanded")
        assert self._is_active(expanded_locator, 3), f"Task {task_id} did not expand"

    def collapse_task(self, task_id):
        """Collapse an expanded task"""
        locator = locator_from_testid(f"task-item-{task_id}-collapse-button")
        self._click(locator)

    def edit_task(self, task_id):
        """Click edit button on a task"""
        # First ensure task is expanded
        if not self._is_displayed(locator_from_testid(f"task-item-{task_id}-edit-button")):
            self.expand_task(task_id)

        edit_button_locator = locator_from_testid(f"task-item-{task_id}-edit-button")
        self._click(edit_button_locator)

        # Wait for edit form to appear
        edit_form_locator = locator_from_testid(f"task-edit-{task_id}-form")
        assert self._is_active(edit_form_locator, 3), f"Task {task_id} edit form did not appear"

    def save_task_edit(self, task_id, title=None, description=None, status=None, active=None):
        """Save changes to a task"""
        if title is not None:
            title_input_locator = locator_from_testid(f"task-edit-{task_id}-title-input")
            self._type(title_input_locator, title)

        if description is not None:
            description_input_locator = locator_from_testid(f"task-edit-{task_id}-description-input")
            self._type(description_input_locator, description)

        if status is not None:
            from selenium.webdriver.support.ui import Select
            status_select_locator = locator_from_testid(f"task-edit-{task_id}-status-select")
            select_element = self._find(status_select_locator)
            select = Select(select_element)
            select.select_by_value(status)

        if active is not None:
            active_checkbox_locator = locator_from_testid(f"task-edit-{task_id}-active-checkbox")
            checkbox = self._find(active_checkbox_locator)
            is_checked = checkbox.is_selected()
            if active and not is_checked:
                self._click(active_checkbox_locator)
            elif not active and is_checked:
                self._click(active_checkbox_locator)

        save_button_locator = locator_from_testid(f"task-edit-{task_id}-save-button")
        self._click(save_button_locator)

    def cancel_task_edit(self, task_id):
        """Cancel editing a task"""
        cancel_button_locator = locator_from_testid(f"task-edit-{task_id}-cancel-button")
        self._click(cancel_button_locator)

    def delete_task(self, task_id):
        """Delete a task (handles confirmation dialog)"""
        delete_button_locator = locator_from_testid(f"task-item-{task_id}-delete-button")
        self._click(delete_button_locator)
        # Note: This will trigger a browser alert in the demo
        # Tests will need to handle the alert separately

    def get_task_title_text(self, task_id):
        """Get the displayed title text of a task"""
        title_locator = locator_from_testid(f"task-item-{task_id}-title")
        element = self._find(title_locator)
        return element.text