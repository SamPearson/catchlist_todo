from selenium.webdriver.common.by import By
from pages.base_page import testid_locator
from pages.base_app_page import BaseAppPage


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
        # self.click(self._new_todo_entry_field)
        self._type(self.todo_input_locator, "party time")
        self._click(self.todo_add_button_locator)

    def todo_list(self):
        todo_list = []
        todo_webelements = self._find_all(self.todo_item_locator)
        for todo in todo_webelements:
            todo_title = self._find_child(todo, self.todo_title_locator).text
            todo_list.append({
                'title': todo_title
            })

        return todo_list

