import pytest


def test_api_health(api_client):
    """Verify the API health endpoint is responding correctly"""
    # Get the raw response
    raw_response = api_client.get('/api/health', handle_response=False)

    # First check the HTTP status code
    assert raw_response.status_code == 200, "API health check failed - non-200 status code"

    # Optionally check the response body if we care about the format
    response = raw_response.json
    assert 'status' in response, "API health response missing 'status' field"
    assert response['status'] in ['healthy', 'ok'], "API health check failed - unexpected status value"


def test_api_health_connection_error(api_client, monkeypatch):
    """Verify we handle API connection failures gracefully"""
    import requests

    def mock_request(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Failed to connect")

    monkeypatch.setattr(api_client._session, "request", mock_request)

    with pytest.raises(Exception) as exc_info:
        api_client.get('/api/health')
    assert "Failed to connect" in str(exc_info.value)