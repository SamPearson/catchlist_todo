import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import random
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path 
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from test_utils.api_client import WebAppTestAPIClient
from pages.login_page import LoginPage
from pages.user_registration_page import RegistrationPage
from pages.user_account_page import AccountPage


def pytest_addoption(parser):
    parser.addoption("--env",
                     action="store",
                     default="local",
                     help="Environment name (e.g., local, staging, production)")
    parser.addoption("--headless",
                     action="store",
                     default="False",
                     help="Run tests with browser in headless mode")


def load_environment(env_name):
    """Load environment variables from .env file"""
    # conftest.py is in test/webapp/, environments folder is sibling to it
    env_file = Path(__file__).parent.parent / "environments" / f".env.{env_name}"
    
    if not env_file.exists():
        raise FileNotFoundError(f"Environment file not found: {env_file}")
    
    load_dotenv(env_file, override=True)


def setup_webdriver(request):
    """
    Helper function to set up a WebDriver with proper configuration
    """
    headless = request.config.getoption("--headless") != "False"
    service = Service()
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=service, options=options)
    
    # Set window size for both headless and non-headless modes
    if headless:
        # In headless mode, we need to set a large window size
        driver.set_window_size(1920, 1080)
    else:
        # In non-headless mode, we can maximize the window
        driver.maximize_window()

    # Load environment variables
    env_name = request.config.getoption("--env")
    load_environment(env_name)

    webapp_url = os.getenv("WEBAPP_URL")
    if not webapp_url:
        raise ValueError("WEBAPP_URL not found in environment file")

    # Parse URL for base_domain (for cookie injection)
    from urllib.parse import urlparse
    parsed = urlparse(webapp_url)
    
    driver.base_url = webapp_url
    driver.base_domain = parsed.hostname

    return driver


def get_api_base_url(request):
    """Get API base URL from environment config"""
    # Load environment if not already loaded
    if not os.getenv("API_BASE_URL"):
        env_name = request.config.getoption("--env")
        load_environment(env_name)
    
    api_base_url = os.getenv("API_BASE_URL")
    if not api_base_url:
        raise ValueError("API_BASE_URL not found in environment file")
    
    return api_base_url


@pytest.fixture(scope="session")
def api_base_url(request):
    """Session-scoped API base URL"""
    return get_api_base_url(request)


@pytest.fixture
def driver(request):
    """Function-scoped driver - new browser instance per test"""
    driver_ = setup_webdriver(request)
    
    # Add environment information to Allure report
    allure.dynamic.description_html(f"""
        <h3>Test Environment</h3>
        <p><b>Browser:</b> Chrome</p>
        <p><b>Headless:</b> {request.config.getoption("--headless")}</p>
        <p><b>Environment:</b> {request.config.getoption("--env")}</p>
    """)

    yield driver_
    
    # Cleanup
    try:
        # Take screenshot on test failure
        if hasattr(request.node, 'result_call') and request.node.result_call.failed:
            allure.attach(
                driver_.get_screenshot_as_png(),
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
    finally:
        driver_.quit()


@pytest.fixture
def api_client(api_base_url):
    """Function-scoped API client - fresh client per test"""
    return WebAppTestAPIClient(api_base_url)


@pytest.fixture
def test_user(api_client):
    """
    Create a fresh test user for each test via API.
    Automatically deleted after test completes.
    """
    # Generate unique credentials
    rand_int = random.randint(0, 99999)
    username = f"test_user{rand_int}"
    password = f"TestPass{rand_int}!"
    
    # Register and login via API
    api_client.register_user(username, password)
    api_client.login_user(username, password)
    
    user_data = {
        "username": username,
        "password": password,
        "token": api_client.token
    }
    
    yield user_data
    
    # Cleanup: Delete user after test
    try:
        # Login again in case test logged out
        if not api_client.token:
            api_client.login_user(username, password)
        api_client.delete_user(password)
    except Exception as e:
        print(f"Failed to delete test user {username}: {e}")


@pytest.fixture
def authenticated_driver(driver, test_user, api_client):
    """
    Provides a driver with authenticated session (cookie injected).
    Fresh user per test.
    """
    # Navigate to app first (cookies require a page to be loaded)
    driver.get(driver.base_url)
    
    # Inject auth cookie
    api_client.inject_auth_cookie(driver)
    
    # Refresh to apply cookie
    driver.refresh()
    
    return driver


@pytest.fixture
def unauthenticated_driver(driver):
    """
    Provides a driver without authentication.
    Useful for testing login flows.
    """
    driver.get(driver.base_url)
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

