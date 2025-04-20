from pages.base_page import testid_locator
from pages.base_app_page import BaseAppPage
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from time import sleep


class TodoListPage(BaseAppPage):
    # input form locators
    todo_form_locator = testid_locator("add-todo-form")
    todo_input_locator = testid_locator("add-todo-input")
    todo_add_button_locator = testid_locator("add-todo-button")

    # to do list
    todo_list_locator = testid_locator("todo-list")
    todo_item_locator = testid_locator("todo-item")

    def __init__(self, driver):
        super().__init__(driver)

    class TodoListItem:
        todo_checkbox_locator = testid_locator("todo-checkbox")
        todo_title_locator = testid_locator("todo-title")
        todo_delete_button_locator = testid_locator("delete-todo-button")

        def __init__(self, outer, element):
            self.outer = outer  # Ref the outer class to access selenium wrapper functions
            self.element = element
            self.todo_id = element.get_attribute('data-id')
            self.title = outer._find_child(element, self.todo_title_locator).text

        # We're storing webelements and giving to-dos the ability to refresh them
        # because there's not another way to confirm edits unless we remember to
        # do so every time we interact with a to-do.
        def refresh(self):
            """Fetch a fresh copy of the webelement based off of the to-do id"""
            if self.is_stale():
                fresh_todos = self.outer._find_all(self.outer.todo_item_locator)
                for todo in fresh_todos:
                    if todo.get_attribute('data-id') == self.todo_id:
                        self.element = todo
                        return True
                raise AssertionError(f"Could not find todo with ID {self.todo_id}")
            return True

        def completed_box_checked(self):
            return self.outer._find_child(self.element, self.todo_checkbox_locator).is_selected()

        def toggle_completed(self):
            self.refresh()
            checkbox = self.outer._find_child(self.element, self.todo_checkbox_locator)
            initial_state = checkbox.is_selected()
            checkbox.click()

            self.refresh()

            # Wait/confirm state change
            self.outer._wait_until(
                lambda d: self.completed_box_checked() != initial_state,
                timeout=5,
                error_message="Failed to toggle completion state"
            )

        def set_completed_state(self, should_be_completed):
            """Explicitly set the completion state to a given value"""
            current_state = self.completed_box_checked()
            if current_state != should_be_completed:
                self.toggle_completed()

        def is_stale(self):
            try:
                # Accessing any property will throw an exception if the element is stale
                self.element.is_enabled()
                return False
            except StaleElementReferenceException:
                return True

        def delete_button(self):
            self.refresh()
            return self.outer._find_child( self.element, self.todo_delete_button_locator)

        def __repr__(self):
            return f"TodoListItem(id={self.todo_id}, title='{self.title}', completed={self.completed_box_checked()})"

    def create_todo(self, title):
        # hold the to-do form, it will go stale after we submit a new to-do
        form_element = self._find(self.todo_form_locator)

        self._type(self.todo_input_locator, title)
        self._click(self.todo_add_button_locator)

        # Expect the to-do form to go stale.
        # if it doesn't go stale in 5 sec, it refreshed before we started waiting.
        self._wait_until(
            lambda d: expected_conditions.staleness_of(form_element)(d),
            timeout=5,
            error_message="Page did not reload after adding todo",
            suppress_timeout=True  # changing this will cause race conditions
        )

        # Now wait for todo list to appear in the new page
        self._is_active(self.todo_list_locator, timeout=5)

    def get_todos(self, retry_count=3):
        try:
            todo_list = []
            for todo_element in self._find_all(self.todo_item_locator):
                todo_obj = self.TodoListItem(self, todo_element)
                todo_list.append(todo_obj)
            return todo_list
        except StaleElementReferenceException:
            # wait a bit and then rerun the function, assuming the DOM has stabilized
            if retry_count > 0:
                sleep(0.2)
                return self.get_todos(retry_count - 1)
            else:
                # Retry count exhausted, reraise the exception
                raise

    def find_todo_by_id(self, todo_id):
        todos = self.get_todos()
        return next((todo for todo in todos if todo.todo_id == todo_id), None)

    def find_todo_by_title(self, title):
        todos = self.get_todos()
        return next((todo for todo in todos if todo.title == title), None)

    def delete_todo(self, todo_object):
        todo_id = todo_object.todo_id
        todo_object.delete_button().click()
        self._wait_until(
            lambda d: self.find_todo_by_id(todo_id) is None,
            timeout=5,
            error_message="Todo still appears to exist after attempting to delete it",
        )

