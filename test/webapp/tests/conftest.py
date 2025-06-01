import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from environments.environment_data import Environment
import os
import random

from pages.login_page import LoginPage
from pages.user_registration_page import RegistrationPage
from pages.user_account_page import AccountPage


def pytest_addoption(parser):
    parser.addoption("--env",
                     action="store",
                     default="no_env",
                     help="Filename for the test environment file")
    parser.addoption("--headless",
                     action="store",
                     default="False",
                     help="Run tests with browser in headless mode")


def setup_webdriver(request):
    """
    Helper function to set up a WebDriver with proper configuration
    """
    headless = request.config.getoption("--headless") != "False"
    service = Service()
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')

        # Magical Config args:
        # SOME(not all) selectors break if you don't set window size. on headless mode.
        options.add_argument('window-size=1920x1080')
        # Browser will not be initialized in bitbucket pipelines without this config argument
        # may be able to get away without it in other platforms.
        options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    test_environment = request.config.getoption("--env")
    test_env_filename = os.path.join("environments", f"{test_environment}")
    assert os.path.exists(test_env_filename), f"Could not find json env file for {test_env_filename}"

    Environment.parse_environment_file(test_env_filename)

    protocol = Environment.get_value("protocol")
    host = Environment.get_value("host")
    port = Environment.get_value("port")

    driver.base_url = f"{protocol}://{host}:{port}"
    driver.base_domain = host

    return driver


@pytest.fixture
def driver(request):
    driver_ = setup_webdriver(request)
    
    # Add environment information to Allure report
    allure.dynamic.description_html(f"""
        <h3>Test Environment</h3>
        <p><b>Browser:</b> Chrome</p>
        <p><b>Headless:</b> {request.config.getoption("--headless")}</p>
        <p><b>Environment:</b> {request.config.getoption("--env")}</p>
    """)

    def quit_browser():
        try:
            # Take screenshot on test failure
            if request.node.result_call.failed:
                allure.attach(
                    driver_.get_screenshot_as_png(),
                    name="failure_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
        finally:
            driver_.quit()

    request.addfinalizer(quit_browser)
    return driver_


@pytest.fixture(scope="session")
def test_user_credentials():
    # tack a random int onto the user and pass to avoid collisions
    # just in case we fail to delete a user somehow.
    session_rand_int = random.randint(0,9999)
    session_username = f"test_user{session_rand_int}"
    session_password = f"test_user{session_rand_int}"

    return {"username": session_username, "password": session_password}


@pytest.fixture(scope="session")
def registered_user(test_user_credentials, request):
    """
    Create a user once before any tests run, to be used for all tests and deleted after
    """
    driver = setup_webdriver(request)

    try:
        registration_page = RegistrationPage(driver)
        registration_page.register_new_user(
            test_user_credentials["username"],
            test_user_credentials["password"]
        )
    finally:
        driver.quit()

    return test_user_credentials


@pytest.fixture
def login(driver, registered_user):
    """
    Fixture to log in before a test begins
    """
    login_page = LoginPage(driver)

    username = registered_user["username"],
    password = registered_user["password"]

    login_page.login(username, password)
    return driver


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    
    # Add test result to Allure report
    if result.when == "call":
        if result.failed:
            allure.attach(
                str(result.longrepr),
                name="failure_details",
                attachment_type=allure.attachment_type.TEXT
            )
    
    setattr(item, "result_" + result.when, result)


@pytest.fixture(scope="session", autouse=True)
def cleanup_registered_user(test_user_credentials, request):
    """
    Cleanup fixture - runs after all tests, deletes the test user
    """
    # yield here so we can run a teardown procedure after all tests
    yield

    # now all tests should be done; log in and delete the user
    driver = setup_webdriver(request)
    username = test_user_credentials["username"],
    password = test_user_credentials["password"]

    try:
        login_page = LoginPage(driver)
        login_page.login(username, password)

        account_page = AccountPage(driver)
        account_page.delete_account(password)
    except Exception as e:
        print(f"Failed to delete test user {username}: {e}")
    finally:
        driver.quit()

