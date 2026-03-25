from typing import Optional, Dict
import requests
import json
import allure
from utils.data_factories.api_user import APIUser


class APIResponse:
    def __init__(self, response: requests.Response):
        self._response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self.elapsed = response.elapsed

        self._json = None
        self._text = response.text

        try:
            self._json = response.json()
        except json.JSONDecodeError:
            pass

    @property
    def json(self) -> dict | None:
        return self._json

    @property
    def text(self) -> str:
        return self._text

    def __getitem__(self, item):
        if self._json is None:
            raise TypeError("Response does not contain JSON")
        return self._json[item]

    def __contains__(self, key):
        """Support 'key in response' syntax."""
        if self._json is None:
            return False
        return key in self._json

    def get(self, key, default=None):
        if self._json is None:
            return default
        return self._json.get(key, default)

    def raise_for_status(self):
        self._response.raise_for_status()


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.current_user: Optional[APIUser] = None

    def diagnose_request(self, request: requests.PreparedRequest) -> str:
        """Generate diagnostic information about a request."""
        info = [
            "=== Request Diagnostics ===",
            f"Method: {request.method}",
            f"URL: {request.url}",
            "\nHeaders:",
            *[f"  {k}: {v}" for k, v in request.headers.items()],
            "\nBody:",
            f"  {request.body if request.body else '(empty)'}"
        ]
        return "\n".join(info)

    def diagnose_response(self, response: requests.Response) -> str:
        """Generate diagnostic information about a response."""
        info = [
            "=== Response Diagnostics ===",
            f"Status: {response.status_code} {response.reason}",
            f"Elapsed Time: {response.elapsed.total_seconds():.3f}s",
            "\nHeaders:",
            *[f"  {k}: {v}" for k, v in response.headers.items()],
            "\nBody:",
        ]

        try:
            # Try to format JSON response
            body = json.dumps(response.json(), indent=2)
            info.append(f"  {body}")
        except json.JSONDecodeError:
            # If not JSON, add raw text (truncated if too long)
            body = response.text
            if len(body) > 1000:
                body = body[:1000] + "... (truncated)"
            info.append(f"  {body}")

        return "\n".join(info)

    def request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                params: Optional[Dict] = None, handle_response: bool = True) -> APIResponse:
        """Send request to specified endpoint."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint.startswith('/') else endpoint

        with allure.step(f"{method.upper()} {endpoint}"):
            # Log request details
            if data:
                allure.attach(
                    json.dumps(data, indent=2),
                    name="Request Body",
                    attachment_type=allure.attachment_type.JSON
                )
            if params:
                allure.attach(
                    json.dumps(params, indent=2),
                    name="Query Parameters",
                    attachment_type=allure.attachment_type.JSON
                )

            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            )

            # Wrap the response
            api_response = APIResponse(response)

            # Log response details
            if api_response.json is not None:
                allure.attach(
                    json.dumps(api_response.json, indent=2),
                    name="Response Body",
                    attachment_type=allure.attachment_type.JSON
                )
            else:
                allure.attach(
                    api_response.text[:1000] if api_response.text else "(empty)",
                    name="Response Body",
                    attachment_type=allure.attachment_type.TEXT
                )

            allure.attach(
                f"Status Code: {api_response.status_code}\nElapsed Time: {api_response.elapsed.total_seconds():.3f}s",
                name="Response Info",
                attachment_type=allure.attachment_type.TEXT
            )

            if not (200 <= api_response.status_code < 300):
                allure.attach(
                    self.diagnose_response(response),
                    name="Error Details",
                    attachment_type=allure.attachment_type.TEXT
                )

            if handle_response:
                api_response.raise_for_status()

            return api_response


    def login(self, user: APIUser) -> APIResponse:
        """Authenticate user and store user object with token."""
        response = self.post('/api/auth/login', {
            'username': user.username,
            'password': user.password
        })

        if 'access_token' in response:
            user.token = response['access_token']
            self.current_user = user
            self.session.headers.update({
                'Authorization': f'Bearer {user.token}'
            })

        return response

    def register(self, user: APIUser) -> APIResponse:
        """Register a new user account."""
        response = self.post('/api/auth/register', {
            'username': user.username,
            'password': user.password
        })

        return response

    def delete_account(self) -> APIResponse:
        """Delete the current user account."""
        if not self.is_authenticated():
            raise ValueError("Must be logged in to delete account")

        response = self.post('/api/auth/delete-account', {
            'password': self.current_user.password
        })

        self.logout()
        return response

    def logout(self) -> None:
        """Clear authentication state."""
        if self.current_user:
            self.current_user.token = None
        self.current_user = None
        self.session.headers.pop('Authorization', None)

    def is_authenticated(self) -> bool:
        """Check if the client is currently authenticated."""
        return self.current_user is not None and self.current_user.is_authenticated


    # HTTP method convenience functions
    def get(self, endpoint: str, params: Optional[Dict] = None, handle_response: bool = True):
        return self.request('get', endpoint, params=params, handle_response=handle_response)

    def post(self, endpoint: str, data: Optional[Dict] = None, handle_response: bool = True):
        return self.request('post', endpoint, data=data, handle_response=handle_response)

    def put(self, endpoint: str, data: Optional[Dict] = None, handle_response: bool = True):
        return self.request('put', endpoint, data=data, handle_response=handle_response)

    def patch(self, endpoint: str, data: Optional[Dict] = None, handle_response: bool = True):
        return self.request('patch', endpoint, data=data, handle_response=handle_response)

    def delete(self, endpoint: str, handle_response: bool = True):
        return self.request('delete', endpoint, handle_response=handle_response)