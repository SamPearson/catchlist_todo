from selenium.webdriver.common.by import By
from pages.base_page import BasePage, testid_locator

class TodoListPage(BasePage):
    _new_todo_entry_field = (By.ID, "todo-entry-title")
    _new_todo_entry_button = (By.ID, "todo-entry-add-button")

    _todo_display_box = testid_locator("todo-display")
    _todo_title = testid_locator("todo-display-header")
    _todo_completed = testid_locator("todo-display-completion")
    _todo_update_button = testid_locator("todo-display-update-button")
    _todo_delete_button = testid_locator("todo-display-delete-button")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit(driver.base_url)

        # I don't have a great way to confirm "the page is loaded".
        # I'm not even sure that's a valid goal compared to more granular "is this element loaded" checks,
        # but I need to somehow confirm we did send a request to a url and get something back besides an error.
        # or do I? shouldn't that error just show up in a screenshot when we fail to find a needed element later?
        import time
        time.sleep(10)

        # assert something that should be present

    def create_todo(self, title):
        # self.click(self._new_todo_entry_field)
        self._type(self._new_todo_entry_field)
        self._click(self._new_todo_entry_button)

    def todo_list(self):
        todo_dicts = []
        todo_webelements = self._find_all(self._todo_display_box)
        for todo in todo_webelements:
            todo_title = self._find_child(todo, self._todo_title).text
            todo_status = self._find_child(todo, self._todo_completed).text
            todo_dicts.append({
                'title': todo_title,
                'status': todo_status
            })

        return todo_dicts

