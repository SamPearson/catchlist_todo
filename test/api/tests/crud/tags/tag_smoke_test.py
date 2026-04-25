import pytest
import allure
from test_utils.data_factories.entity_factory import create_task


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_basic_tag(auth_client):
    """Create a basic tag with only name"""

    with allure.step("Create tag with only name"):
        payload = {
            "name": "work"
        }
        response = auth_client.post('/api/tags', data=payload)

    with allure.step("Verify tag created successfully"):
        assert response['id']
        assert response['name'] == "work"
        assert response['color'] == "#6c757d"  # Default gray
        assert response['user_id']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Tags')
@allure.story('List Tags')
@pytest.mark.tags
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_tags(auth_client):
    """List tags verifies tag appears"""

    with allure.step("Create a tag"):
        tag = auth_client.post('/api/tags', data={"name": "urgent"})
        tag_id = tag['id']

    with allure.step("List all tags"):
        response = auth_client.get('/api/tags')

    with allure.step("Verify created tag appears in list"):
        assert isinstance(response.json, list)
        tag_ids = [t['id'] for t in response.json]
        assert tag_id in tag_ids


@allure.feature('Tags')
@allure.story('Get Tag')
@pytest.mark.tags
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_tag_by_id(auth_client):
    """Get tag by ID returns full tag object"""

    with allure.step("Create a tag"):
        created = auth_client.post('/api/tags', data={"name": "health"})
        tag_id = created['id']

    with allure.step("Retrieve tag by ID"):
        response = auth_client.get(f'/api/tags/{tag_id}')

    with allure.step("Verify tag object returned"):
        assert response['id'] == tag_id
        assert response['name'] == "health"
        assert response['color']
        assert response['user_id']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_tag_name(auth_client):
    """Update tag name"""

    with allure.step("Create a tag"):
        created = auth_client.post('/api/tags', data={"name": "learning"})
        tag_id = created['id']

    with allure.step("Update tag name"):
        payload = {
            "name": "education"
        }
        response = auth_client.patch(f'/api/tags/{tag_id}', data=payload)

    with allure.step("Verify name updated"):
        assert response['id'] == tag_id
        assert response['name'] == "education"


@allure.feature('Tags')
@allure.story('Delete Tag')
@pytest.mark.tags
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_tag(auth_client):
    """Delete tag returns 204 and removes tag"""

    with allure.step("Create a tag"):
        created = auth_client.post('/api/tags', data={"name": "temporary"})
        tag_id = created['id']

    with allure.step("Delete tag"):
        response = auth_client.delete(f'/api/tags/{tag_id}', handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204

    with allure.step("Verify tag no longer exists"):
        get_response = auth_client.get(f'/api/tags/{tag_id}', handle_response=False)
        assert get_response.status_code == 404