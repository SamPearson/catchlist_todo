from pages.base_app_page import BaseAppPage
from pages.base_page import locator_from_testid
from pages.components.task_item_component import TaskItemComponent
from pages.components.task_search_component import TaskSearchComponent
from pages.components.task_create_component import TaskCreateComponent


class TaskComponentDemoPage(BaseAppPage):
    # Page sections
    search_section_locator = locator_from_testid("demo-search-section")
    create_section_locator = locator_from_testid("demo-create-section")
    tasks_section_locator = locator_from_testid("demo-tasks-section")

    # Task created notification (demo-specific, not part of component)
    task_created_notification_locator = locator_from_testid("demo-task-created-notification")
    reset_create_button_locator = locator_from_testid("demo-reset-create-button")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/component-demo/tasks")

    # ============================================================================
    # COMPONENT FACTORIES
    # ============================================================================
    
    def get_task(self, task_id):
        """Get a TaskItemComponent for interacting with a specific task.
        
        Args:
            task_id: The ID of the task to interact with
        
        Returns:
            TaskItemComponent: Component object for the task
        """
        return TaskItemComponent(self.driver, task_id)
    
    def get_search(self):
        """Get the TaskSearchComponent for interacting with search/filters.
        
        Returns:
            TaskSearchComponent: Component object for search
        """
        return TaskSearchComponent(self.driver)
    
    def get_create_form(self):
        """Get the TaskCreateComponent for interacting with the create form.
        
        Returns:
            TaskCreateComponent: Component object for task creation
        """
        return TaskCreateComponent(self.driver)

    # ============================================================================
    # DEMO PAGE SPECIFIC METHODS
    # ============================================================================
    
    def reset_create_form(self):
        """Reset the create form to create another task.
        
        This is specific to the demo page - clicks the reset button
        that appears after successful task creation.
        """
        self._click(self.reset_create_button_locator)
    
    def is_task_created_notification_displayed(self):
        """Check if the task creation success notification is displayed.
        
        This is specific to the demo page.
        
        Returns:
            bool: True if notification is displayed
        """
        return self._is_displayed(self.task_created_notification_locator, timeout=5)