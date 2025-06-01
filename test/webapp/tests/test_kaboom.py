import pytest
from pages import desk_page
import allure


@allure.feature("Kaboom")
@allure.story("Kaboom")
@pytest.mark.smoke
class TestTodoCrud:
    @pytest.fixture
    def page(self, login):
        return desk_page.DeskPage(login)

    def test_kaboom(self, page):
        page.kaboom()
