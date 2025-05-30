import pytest
from pages import todo_list_page


@pytest.mark.deprecated
class TestTodoCrud:
    @pytest.fixture
    def page(self, login):
        return todo_list_page.TodoListPage(login)

    def test_create_todo(self, page):
        todo_name = "test_todo_name"
        page.create_todo(todo_name)

    def test_delete_todo(self, page):
        todo_name = "deleteme"
        page.create_todo(todo_name)
        todo_obj = page.find_todo_by_title(todo_name)
        page.delete_todo(todo_obj)

    def test_update_todo(self, page):
        todo_name = "updateme"
        page.create_todo(todo_name)
        todo_obj = page.find_todo_by_title(todo_name)
        completed_status = todo_obj.completed_box_checked()
        todo_obj.toggle_completed()
        assert completed_status != todo_obj.completed_box_checked(), "could not update todo status"

