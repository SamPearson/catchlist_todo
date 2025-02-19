
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from environments import environment_data
import os


def pytest_addoption(parser):
    parser.addoption("--baseurl",
                     action="store",
                     default="the-internet.herokuapp.com",
                     help="base URL for the application under test")
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
    test_env_filename = os.path.join("environments", f"{test_environment}.json")
    assert os.path.exists(test_env_filename), f"Could not find json env file for {test_env_filename}"

    environment_data.parse_environment_file(test_env_filename)

    # This should be set by the env file or by the test type
    url_option = request.config.getoption("--baseurl")
    if url_option.startswith('http'):
        driver_.base_url = url_option
    else:
        driver_.base_url = "https://" + url_option

    driver_.base_domain = request.config.getoption("--baseurl")

    def quit_browser():
        driver_.quit()

    request.addfinalizer(quit_browser)
    return driver_


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    setattr(item, "result_" + result.when, result)
