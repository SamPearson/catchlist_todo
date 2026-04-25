from typing import Optional
import sys
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver

# Add project root to path (4 levels up from this file)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.api_client import BaseAPIClient


class WebAppTestAPIClient(BaseAPIClient):
    """
    API client for webapp UI testing.
    Provides methods for test user lifecycle and cookie injection.
    """

    def __init__(self, base_url: str):
        # Use session to maintain state during test setup/teardown
        super().__init__(base_url, use_session=True)
        self._username: Optional[str] = None
        self._password: Optional[str] = None

    def register_user(self, username: str, password: str) -> dict:
        """
        Register a new test user.

        Args:
            username: Username for new user
            password: Password for new user

        Returns:
            Response data from registration endpoint
        """
        response = self.post('/api/auth/register', {
            'username': username,
            'password': password
        })

        # Store credentials for later use
        self._username = username
        self._password = password

        return response

    def login_user(self, username: str, password: str) -> dict:
        """
        Log in and retrieve authentication token.

        Args:
            username: Username
            password: Password

        Returns:
            Response data containing access_token
        """
        response = self.post('/api/auth/login', {
            'username': username,
            'password': password
        })

        if response and 'access_token' in response:
            self.token = response['access_token']
            self._username = username
            self._password = password

        return response

    def delete_user(self, password: Optional[str] = None) -> dict:
        """
        Delete the current test user account.

        Args:
            password: Password for account deletion (uses stored password if not provided)

        Returns:
            Response data from delete endpoint
        """
        if not self.token:
            raise ValueError("Must be logged in to delete account")

        pwd = password or self._password
        if not pwd:
            raise ValueError("Password required for account deletion")

        response = self.post('/api/auth/delete-account', {
            'password': pwd
        })

        # Clear stored credentials
        self.token = None
        self._username = None
        self._password = None

        return response

    def inject_auth_cookie(self, driver: WebDriver, domain: Optional[str] = None):
        """
        Inject authentication token as cookie into Selenium WebDriver.

        Args:
            driver: Selenium WebDriver instance
            domain: Optional domain for cookie (defaults to driver.base_domain if available)
        """
        if not self.token:
            raise ValueError("No authentication token available. Call login_user() first.")

        # Get domain from driver if available
        cookie_domain = domain or getattr(driver, 'base_domain', None)

        cookie_data = {
            'name': 'auth_token',
            'value': self.token
        }

        if cookie_domain:
            cookie_data['domain'] = cookie_domain

        driver.add_cookie(cookie_data)

    def create_and_inject_user(self, driver: WebDriver, username: str, password: str,
                               domain: Optional[str] = None) -> dict:
        """
        Convenience method to register user, login, and inject cookie in one call.

        Args:
            driver: Selenium WebDriver instance
            username: Username for new user
            password: Password for new user
            domain: Optional domain for cookie

        Returns:
            Login response data
        """
        self.register_user(username, password)
        login_response = self.login_user(username, password)
        self.inject_auth_cookie(driver, domain)
        return login_response