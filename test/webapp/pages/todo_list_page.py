from pages.base_page import testid_locator
from pages.base_app_page import BaseAppPage
from selenium.webdriver.support import expected_conditions


class TodoListItem:
    def __init__(self, todo_id, title, completed):
        self.todo_id = todo_id
        self.title = title
        self.completed = completed

    def __repr__(self):
        return f"TodoListItem(id={self.todo_id}, title='{self.title}', completed={self.completed})"


class TodoListPage(BaseAppPage):
    # input form locators
    todo_form_locator = testid_locator("add-todo-form")
    todo_input_locator = testid_locator("add-todo-input")
    todo_add_button_locator = testid_locator("add-todo-button")

    # to do list
    todo_list_locator = testid_locator("todo-list")
    # individual to dos
    todo_item_locator = testid_locator("todo-item")
    todo_checkbox_locator = testid_locator("todo-checkbox")
    todo_title_locator = testid_locator("todo-title")
    todo_delete_button_locator = testid_locator("delete-todo-button")

    def __init__(self, driver):
        super().__init__(driver)

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

    def get_todos(self):
        todo_list = []

        for todo in self._find_all(self.todo_item_locator):
            todo_title = self._find_child(todo, self.todo_title_locator).text
            todo_id = todo.get_attribute('data-id')
            completed_checkbox = self._find_child(todo, self.todo_checkbox_locator)
            completed_value = completed_checkbox.is_selected()

            new_todo = TodoListItem(todo_id, todo_title, completed_value)

            todo_list.append(new_todo)

        return todo_list

    def find_todo_by_id(self, todo_id):
        todos = self.get_todos()
        todo = next((todo for todo in todos if todo.todo_id == todo_id), None)
        assert todo, f"Could not find todo with ID '{todo_id}'"
        return todo

    def find_todo_by_title(self, title):
        todos = self.get_todos()
        from pprint import pprint
        todo = next((todo for todo in todos if todo.title == title), None)
        assert todo, f"Could not find todo with title '{title}'"
        return todo
