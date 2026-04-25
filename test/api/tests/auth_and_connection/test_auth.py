import pytest
import requests

from test_utils.data_factories.api_user import APIUserFactory



#
# def test_login_failure(api_client):
#     """Test login with invalid credentials"""
#     with pytest.raises(Exception) as exc_info:
#         api_client.login(username="invalid_user", password="invalid_pass")
#
#     assert not api_client.is_authenticated()
#     assert api_client.token is None
#
#

def test_register_success(api_client):
    """Test successful user registration and subsequent login"""
    # Create a new random user
    user = APIUserFactory.create()

    # Register new user
    response = api_client.register(user)
    assert response['message'] == 'User created successfully'
    assert not api_client.is_authenticated()

    login_response = api_client.login(user)
    assert 'access_token' in login_response
    assert api_client.is_authenticated()
    assert user.is_authenticated

    # Clean up by deleting the user
    api_client.delete_account()


# def test_delete_account_success(authenticated_client):
#     """Test successful account deletion"""
#     response = authenticated_client.delete_account(password="test_pass")
#
#     assert not authenticated_client.is_authenticated()
#     assert authenticated_client.token is None
#     assert 'Authorization' not in authenticated_client.session.headers
#
#


#
# def test_register_duplicate_user(api_client):
#     """Test registration with existing username"""
#     # First register a user
#     api_client.register(username="duplicate_user", password="test_pass")
#     api_client.logout()  # Clear the session
#
#     # Try to register the same username again
#     with pytest.raises(Exception) as exc_info:
#         api_client.register(username="duplicate_user", password="different_pass")
#
#

# def test_delete_account_not_logged_in(api_client):
#     """Test account deletion when not logged in"""
#     api_client.logout()  # Ensure we're logged out
#
#     with pytest.raises(ValueError) as exc_info:
#         api_client.delete_account(password="test_pass")
#
#     assert str(exc_info.value) == "Must be logged in to delete account"
#
#
# def test_logout(authenticated_client):
#     """Test logout functionality"""
#     assert authenticated_client.is_authenticated()  # Verify we start authenticated
#
#     authenticated_client.logout()
#
#     assert not authenticated_client.is_authenticated()
#     assert authenticated_client.token is None
#     assert 'Authorization' not in authenticated_client.session.headers
#
#
# def test_authenticated_request(authenticated_client):
#     """Test that requests after login include the auth token"""
#     response = authenticated_client.get('/api/some-protected-endpoint', handle_response=False)
#
#     assert response.request.headers.get('Authorization', '').startswith('Bearer ')
#
#
# def test_connection_error(api_client, monkeypatch):
#     """Test handling of connection errors"""
#
#     def mock_request(*args, **kwargs):
#         raise requests.exceptions.ConnectionError("Failed to connect")
#
#     monkeypatch.setattr(api_client.session, "request", mock_request)
#
#     with pytest.raises(Exception) as exc_info:
#         api_client.login(username="test_user", password="test_pass")
#     assert "Failed to connect" in str(exc_info.value)


@pytest.fixture(autouse=True)
def cleanup_after_test(api_client):
    """Ensure client is logged out after each test"""
    yield
    api_client.logout()