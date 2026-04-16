import os
import requests
from .auth import get_auth_token


class APIClient:
    def __init__(self):
        self.base_url = os.getenv('API_URL', 'http://localhost:5001')  # Default to localhost:5001
        if not self.base_url:
            raise ValueError("API_URL environment variable not set")

    def _get_headers(self, token=None):
        """Get headers with auth token"""
        headers = {'Content-Type': 'application/json'}
        token = token or get_auth_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    def get(self, endpoint, token=None, params=None):
        """Make GET request to API"""
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(token),
            params=params

        )
        return response.json() if response.ok else None

    def post(self, endpoint, data, token=None):
        """Make POST request to API"""
        response = requests.post(
            f"{self.base_url}{endpoint}",
            json=data,
            headers=self._get_headers(token)
        )
        return response.json()

    def put(self, endpoint, data, token=None):
        """Make PUT request to API"""
        response = requests.put(
            f"{self.base_url}{endpoint}",
            json=data,
            headers=self._get_headers(token)
        )
        return response.json()

    def delete(self, endpoint, token=None):
        """Make DELETE request to API"""
        response = requests.delete(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(token)
        )
        # For 204 No Content responses, return None instead of trying to parse JSON
        if response.status_code == 204:
            return None
        return response.json() if response.ok else None


# Create global API client instance
api_client = APIClient()


