import pytest
from pages import todo_list_page


@pytest.mark.smoke
class TestLogin:
    @pytest.fixture
    def page(self, driver):
        return todo_list_page.TodoListPage(driver)

    @pytest.mark.smoke
    def test_read_todos(self, page):
        todos = page.todo_list()
        from pprint import pprint
        pprint(todos)

