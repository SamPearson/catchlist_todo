
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from environments.environment_data import Environment
import os

from pages.login_page import LoginPage


def pytest_addoption(parser):
    parser.addoption("--env",
                     action="store",
                     default="no_env",
                     help="Filename for the test environment file")
    parser.addoption("--headless",
                     action="store",
                     default="False",
                     help="Run tests with browser in headless mode")


@pytest.fixture
def driver(request):
    service = Service()
    options = webdriver.ChromeOptions()
    if request.config.getoption("--headless") != "False":
        options.add_argument('--headless')

        # Magical Config args:
        # SOME(not all) selectors break if you don't set window size. on headless mode.
        options.add_argument('window-size=1920x1080')
        # Browser will not be initialized in bitbucket pipelines without this config argument
        options.add_argument('--no-sandbox')

    driver_ = webdriver.Chrome(service=service, options=options)
    driver_.maximize_window()

    test_environment = request.config.getoption("--env")
    test_env_filename = os.path.join("environments", f"{test_environment}")
    assert os.path.exists(test_env_filename), f"Could not find json env file for {test_env_filename}"

    Environment.parse_environment_file(test_env_filename)

    # Construct the base URL dynamically from the environment file.
    protocol = Environment.get_value("protocol")
    host = Environment.get_value("host")
    port = Environment.get_value("port")

    driver_.base_url = f"{protocol}://{host}:{port}"
    # sometimes we still need the raw hostname.
    # better to just store it now instead of trying to regex it out later.
    driver_.base_domain = host

    def quit_browser():
        driver_.quit()

    request.addfinalizer(quit_browser)
    return driver_


@pytest.fixture
def login(driver):
    """
    Fixture to log in before a test begins
    """
    login_page = LoginPage(driver)
    login_page._visit(driver.base_url)

    username = "lelda"
    password = "lelda"
    login_page.login(username, password)
    return driver


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    setattr(item, "result_" + result.when, result)
