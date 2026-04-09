import pytest
import allure
from utils.data_factories.entity_factory import create_task


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_basic_principle(auth_client):
    """Create a basic principle with only title"""

    with allure.step("Create principle with only title"):
        payload = {
            "title": "Be dependable"
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify principle created successfully"):
        assert response['id']
        assert response['title'] == "Be dependable"
        assert response['color'] == "#ffd700"  # Default gold
        assert response['user_id']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Principles')
@allure.story('List Principles')
@pytest.mark.principles
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_principles(auth_client):
    """List principles verifies principle appears"""

    with allure.step("Create a principle"):
        principle = auth_client.post('/api/principles', data={"title": "Prioritize health"})
        principle_id = principle['id']

    with allure.step("List all principles"):
        response = auth_client.get('/api/principles')

    with allure.step("Verify created principle appears in list"):
        assert isinstance(response.json, list)
        principle_ids = [p['id'] for p in response.json]
        assert principle_id in principle_ids


@allure.feature('Principles')
@allure.story('Get Principle')
@pytest.mark.principles
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_principle_by_id(auth_client):
    """Get principle by ID returns full principle object"""

    with allure.step("Create a principle"):
        created = auth_client.post('/api/principles', data={"title": "Continuous learning"})
        principle_id = created['id']

    with allure.step("Retrieve principle by ID"):
        response = auth_client.get(f'/api/principles/{principle_id}')

    with allure.step("Verify principle object returned"):
        assert response['id'] == principle_id
        assert response['title'] == "Continuous learning"
        assert response['color']
        assert response['user_id']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_principle_title(auth_client):
    """Update principle title"""

    with allure.step("Create a principle"):
        created = auth_client.post('/api/principles', data={"title": "Financial security"})
        principle_id = created['id']

    with allure.step("Update principle title"):
        payload = {
            "title": "Financial independence"
        }
        response = auth_client.put(f'/api/principles/{principle_id}', data=payload)

    with allure.step("Verify title updated"):
        assert response['id'] == principle_id
        assert response['title'] == "Financial independence"


@allure.feature('Principles')
@allure.story('Delete Principle')
@pytest.mark.principles
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_principle(auth_client):
    """Delete principle returns 204 and removes principle"""

    with allure.step("Create a principle"):
        created = auth_client.post('/api/principles', data={"title": "Temporary principle"})
        principle_id = created['id']

    with allure.step("Delete principle"):
        response = auth_client.delete(f'/api/principles/{principle_id}', handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204

    with allure.step("Verify principle no longer exists"):
        get_response = auth_client.get(f'/api/principles/{principle_id}', handle_response=False)
        assert get_response.status_code == 404