import pytest
from pages import desk_page


@pytest.mark.smoke
class TestTodoCrud:
    @pytest.fixture
    def page(self, login):
        return desk_page.DeskPage(login)

    def test_kaboom(self, page):
        page.kaboom()
        from time import sleep
        sleep(5)
