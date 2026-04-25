import os
from utils.api_client import BaseAPIClient
from .auth import get_auth_token


class WebAppAPIClient(BaseAPIClient):
    """
    API client for webapp server-side rendering.
    Integrates with Flask's cookie/header authentication.
    """
    
    def __init__(self):
        base_url = os.getenv('API_URL', 'http://localhost:5001')
        if not base_url:
            raise ValueError("API_URL environment variable not set")
        
        # Don't use session for webapp - each request is independent
        super().__init__(base_url, use_session=False)
    
    def _get_headers(self, token=None):
        """
        Override to integrate with Flask's get_auth_token helper.
        Falls back to Flask request context if no token provided.
        """
        headers = {'Content-Type': 'application/json'}
        
        # Use provided token, or get from Flask request context
        auth_token = token or get_auth_token()
        
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        return headers


# Create global API client instance
api_client = WebAppAPIClient()


