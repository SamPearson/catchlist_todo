from typing import Optional, Dict, Any
import requests


class BaseAPIClient:
    """
    Base API client with core HTTP functionality.
    Designed to be inherited by specialized clients for different use cases.
    """

    def __init__(self, base_url: str, use_session: bool = False):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for API requests
            use_session: If True, use requests.Session to maintain state across requests
        """
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session() if use_session else None
        self._token: Optional[str] = None

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token."""
        return self._token

    @token.setter
    def token(self, value: Optional[str]):
        """
        Set the authentication token and update session headers if using session.

        Args:
            value: JWT token or None to clear authentication
        """
        self._token = value
        if self._session:
            if value:
                self._session.headers.update({'Authorization': f'Bearer {value}'})
            else:
                self._session.headers.pop('Authorization', None)

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """
        Build headers for request.

        Args:
            token: Optional token to override the instance token

        Returns:
            Dictionary of headers
        """
        headers = {'Content-Type': 'application/json'}

        # Use provided token, fall back to instance token
        auth_token = token if token is not None else self._token

        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'

        return headers

    def _make_request(self, method: str, endpoint: str,
                      data: Optional[Dict] = None,
                      params: Optional[Dict] = None,
                      token: Optional[str] = None) -> requests.Response:
        """
        Internal method to make HTTP request.

        Args:
            method: HTTP method (get, post, put, patch, delete)
            endpoint: API endpoint (with or without leading slash)
            data: Optional request body data
            params: Optional query parameters
            token: Optional token to override instance token

        Returns:
            requests.Response object
        """
        # Build full URL
        if endpoint.startswith('http'):
            # Full URL provided (for special cases)
            url = endpoint
        else:
            # Relative endpoint
            url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Get headers
        headers = self._get_headers(token)

        # Use session if available, otherwise use requests directly
        requester = self._session if self._session else requests

        response = requester.request(
            method=method.upper(),
            url=url,
            json=data,
            params=params,
            headers=headers
        )

        return response

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle response and return appropriate data.
        Can be overridden by subclasses for custom response handling.

        Args:
            response: requests.Response object

        Returns:
            JSON dict if successful and contains JSON, None otherwise
        """
        # Handle 204 No Content
        if response.status_code == 204:
            return None

        # Try to parse JSON for successful responses
        if response.ok:
            try:
                return response.json()
            except ValueError:
                # Response doesn't contain JSON
                return None

        # For error responses, also return None by default
        # Subclasses can override this behavior
        return None

    def request(self, method: str, endpoint: str,
                data: Optional[Dict] = None,
                params: Optional[Dict] = None,
                token: Optional[str] = None,
                handle_response: bool = True) -> Any:
        """
        Make HTTP request to API.

        Args:
            method: HTTP method (get, post, put, patch, delete)
            endpoint: API endpoint
            data: Optional request body data
            params: Optional query parameters
            token: Optional token to override instance token
            handle_response: If True, raise exception on error status codes

        Returns:
            Response data (type depends on subclass implementation of _handle_response)
        """
        response = self._make_request(method, endpoint, data, params, token)

        if handle_response:
            response.raise_for_status()

        return self._handle_response(response)

    # Convenience methods for HTTP verbs

    def get(self, endpoint: str, params: Optional[Dict] = None,
            token: Optional[str] = None, handle_response: bool = True) -> Any:
        """Make GET request to API."""
        return self.request('GET', endpoint, params=params, token=token,
                            handle_response=handle_response)

    def post(self, endpoint: str, data: Optional[Dict] = None,
             params: Optional[Dict] = None, token: Optional[str] = None,
             handle_response: bool = True) -> Any:
        """Make POST request to API."""
        return self.request('POST', endpoint, data=data, params=params,
                            token=token, handle_response=handle_response)

    def put(self, endpoint: str, data: Optional[Dict] = None,
            params: Optional[Dict] = None, token: Optional[str] = None,
            handle_response: bool = True) -> Any:
        """Make PUT request to API."""
        return self.request('PUT', endpoint, data=data, params=params,
                            token=token, handle_response=handle_response)

    def patch(self, endpoint: str, data: Optional[Dict] = None,
              params: Optional[Dict] = None, token: Optional[str] = None,
              handle_response: bool = True) -> Any:
        """Make PATCH request to API."""
        return self.request('PATCH', endpoint, data=data, params=params,
                            token=token, handle_response=handle_response)

    def delete(self, endpoint: str, params: Optional[Dict] = None,
               token: Optional[str] = None, handle_response: bool = True) -> Any:
        """Make DELETE request to API."""
        return self.request('DELETE', endpoint, params=params, token=token,
                            handle_response=handle_response)