import pytest
from pages.task_component_demo_page import TaskComponentDemoPage



@pytest.fixture
def page(authenticated_driver):
    """Navigate to the task component demo page"""
    return TaskComponentDemoPage(authenticated_driver)

@pytest.mark.skip(reason="Demo component tests - real tests needed for API-connected tasks page")
@pytest.mark.smoke
class TestTaskCreate:
    """Tests for the task creation component"""

    def test_create_task_with_title_only(self, page):
        """Test creating a task with just a title"""
        create_form = page.get_create_form()

        task_title = "Test task with title only"
        create_form.create_task(task_title)

        # Verify success notification appears (demo page specific)
        assert page.is_task_created_notification_displayed(), \
            "Task creation success notification not displayed"

    def test_create_task_with_all_fields(self, page):
        """Test creating a task with all fields populated"""
        create_form = page.get_create_form()
        task_title = "Complete task with all fields"
        task_description = "This is a detailed description of the task"

        create_form.create_task(
            title=task_title,
            description=task_description,
            status="waiting",
            active=False
        )

        # Verify success notification appears
        assert page.is_task_created_notification_displayed(), \
            "Task creation success notification not displayed"

    def test_create_task_validation_empty_title(self, page):
        """Test that empty title shows validation error"""
        create_form = page.get_create_form()
        
        # Try to submit without entering a title
        create_form.submit()

        # Verify the validation error message appears
        assert create_form.has_title_error(), \
            "Title validation error not displayed"

        error_message = create_form.get_title_error_text()
        assert error_message == 'Title is required', \
            f"Unexpected error message: {error_message}"

    def test_cancel_task_creation(self, page):
        """Test canceling task creation clears the form"""
        create_form = page.get_create_form()
        
        create_form.set_title("Task to be cancelled")
        create_form.set_description("This will be cancelled")
        create_form.cancel()

        # Verify form is cleared
        assert create_form.get_title_value() == '', "Title field was not cleared"

    def test_reset_after_task_creation(self, page):
        """Test resetting the form after creating a task"""
        create_form = page.get_create_form()
        
        create_form.create_task("Task to reset after")

        # Reset to create another task (demo page specific)
        page.reset_create_form()

        # Verify we're back to the create form
        assert create_form.is_form_displayed(), \
            "Create form did not reappear after reset"

@pytest.mark.skip(reason="Demo component tests - real tests needed for API-connected tasks page")
@pytest.mark.smoke
class TestTaskSearch:
    """Tests for the task search component"""

    def test_simple_search(self, page):
        """Test performing a simple search"""
        search = page.get_search()
        search_query = "running shoes"
        search.simple_search(search_query)
        
        # Verify alert appears with expected text
        alert_text = page._get_alert_text(timeout=3)
        assert 'running shoes' in alert_text, f"Search query not in alert text: {alert_text}"
        page._accept_alert()

    def test_expand_advanced_search(self, page):
        """Test expanding to advanced search view"""
        search = page.get_search()
        search.expand()
        
        # Verify advanced search form is visible
        assert search.is_expanded(), "Advanced search form not displayed"

    def test_collapse_advanced_search(self, page):
        """Test collapsing back to simple search"""
        search = page.get_search()
        search.expand()
        search.collapse()
        
        # Verify we're back to simple search
        assert search.is_collapsed(), "Did not collapse to simple search"

    def test_advanced_search_with_title(self, page):
        """Test advanced search with title filter"""
        search = page.get_search()
        search.advanced_search(title="email")
        
        # Verify alert appears with the filter information
        alert_text = page._get_alert_text(timeout=3)
        assert 'email' in alert_text, f"Filter value not in alert: {alert_text}"
        assert 'Title contains' in alert_text, f"Filter type not in alert: {alert_text}"
        page._accept_alert()
        
        # Verify we collapsed back to simple view
        assert search.is_collapsed(), "Advanced search did not collapse after applying filters"

    def test_advanced_search_with_status_filters(self, page):
        """Test advanced search with status checkboxes"""
        search = page.get_search()
        search.advanced_search(statuses=['open', 'waiting'])
        
        # Handle the alert
        alert_text = page._get_alert_text(timeout=3)
        assert 'open' in alert_text.lower(), f"'open' status not in alert: {alert_text}"
        assert 'waiting' in alert_text.lower(), f"'waiting' status not in alert: {alert_text}"
        page._accept_alert()

    def test_advanced_search_with_active_status(self, page):
        """Test advanced search with active status filter"""
        search = page.get_search()
        search.advanced_search(active_status='active')
        
        # Handle the alert
        alert_text = page._get_alert_text(timeout=3)
        assert 'active' in alert_text.lower(), f"Active status not in alert: {alert_text}"
        page._accept_alert()

    def test_advanced_search_with_completion_status(self, page):
        """Test advanced search with completion status filter"""
        search = page.get_search()
        search.advanced_search(completion_status='complete')
        
        # Handle the alert
        alert_text = page._get_alert_text(timeout=3)
        assert 'complete' in alert_text.lower(), f"Completion status not in alert: {alert_text}"
        page._accept_alert()

    def test_clear_filters(self, page):
        """Test clearing all search filters"""
        search = page.get_search()
        
        # Set up a simple search first
        search.simple_search("test search")
        page._accept_alert()  # Handle the search alert
        
        # Clear filters
        search.clear_filters()

        # Verify simple search input is cleared
        assert search.get_simple_search_value() == '', "Search input was not cleared"


@pytest.mark.skip(reason="Demo component tests - real tests needed for API-connected tasks page")
@pytest.mark.smoke
class TestTaskItems:
    """Tests for the task item/manager components"""

    def test_expand_task_item(self, page):
        """Test expanding a task to see details"""
        task = page.get_task(1)
        task.expand()

        # Verify expanded view is shown
        assert task.is_expanded(), "Task did not expand"

    def test_collapse_task_item(self, page):
        """Test collapsing an expanded task"""
        task = page.get_task(1)
        task.expand()
        task.collapse()

        # Verify minimized view is shown again
        assert task.is_minimized(timeout=3), "Task did not return to minimized state"

    def test_edit_task_flow(self, page):
        """Test the full edit flow: expand, edit, save"""
        task = page.get_task(1)
        
        # Get original title from minimized state
        original_title = task.get_title_from_minimized()

        # Edit the task with new title
        new_title = "Updated task title"
        task.edit_and_save(title=new_title)

        # Collapse to get fresh title from minimized view
        task.collapse()
        
        # Verify the title has changed
        updated_title = task.get_title_from_minimized()
        assert updated_title == new_title, \
            f"Task title was not updated. Expected: '{new_title}', Got: '{updated_title}'"
        assert updated_title != original_title, \
            f"Task title did not change from original value: '{original_title}'"

    def test_cancel_task_edit(self, page):
        """Test canceling task edit returns to view mode"""
        task = page.get_task(1)
        
        task.enter_edit_mode()
        assert task.is_in_edit_mode(), "Task did not enter edit mode"

        task.cancel_edit()
        assert task.is_in_view_mode(timeout=3), "Task did not return to view mode after cancel"

    def test_edit_task_change_status(self, page):
        """Test changing task status"""
        task = page.get_task(1)
        
        # Change status to "deferred"
        task.edit_and_save(status="deferred")
        
        # Verify the status changed
        assert task.verify_status("deferred"), \
            "Task status was not updated to 'deferred'"

    def test_edit_task_toggle_active(self, page):
        """Test toggling task active status"""
        task = page.get_task(1)
        
        # Toggle active status to False (someday/maybe)
        task.edit_and_save(active=False)
        
        # Verify task is now inactive
        details = task.get_details()
        assert not details['is_active'], "Task should be inactive (someday/maybe)"
        
        # Verify "Activate" button is present
        assert task.has_activate_button(), \
            "Activate button not displayed for inactive task"

    def test_view_subtask(self, page):
        """Test that subtask displays correctly with project badge"""
        task = page.get_task(4)  # This is the subtask in the demo
        task.expand()
        
        # Verify task is expanded
        assert task.is_expanded(), "Task did not expand"
        
        # Verify subtask badge is visible
        assert task.has_subtask_badge(), \
            "Subtask badge not displayed for task"


