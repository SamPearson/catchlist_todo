import pytest
from config.environments.environment_manager import EnvironmentManager
from utils.api_client.api_client import APIClient
from utils.data_factories.api_user import APIUserFactory


def pytest_addoption(parser):
    parser.addoption("--env", default="dev", help="Environment: dev/staging/prod")


@pytest.fixture(scope="session")
def env_manager(request):
    manager = EnvironmentManager()
    manager.initialize(request.config.getoption("--env"))
    return manager


@pytest.fixture(scope="session")
def api_client(env_manager):
    return APIClient(env_manager.base_url)


@pytest.fixture(scope="session")
def test_user(api_client):
    """Create and register a test user for the session"""
    user = APIUserFactory.create()
    api_client.register(user)

    yield user

    # Cleanup: Delete test user
    try:
        api_client.login(user)
        api_client.delete_account()
    except Exception as e:
        print(f"Failed to delete test user {user.username}: {e}")


@pytest.fixture
def auth_client(api_client, test_user):
    """Provide authenticated client for tests"""
    api_client.login(test_user)
    yield api_client
    api_client.logout()


def pytest_collection_modifyitems(items):
    """Run heartbeat and setup tests first"""
    heartbeat = []
    setup = []
    other = []

    for item in items:
        if "test_api_health" in item.name:
            heartbeat.append(item)
        elif "test_register" in item.name:
            setup.append(item)
        else:
            other.append(item)

    items[:] = heartbeat + setup + other