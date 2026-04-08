import pytest
import allure


@allure.feature('Tags')
@allure.story('Get Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_tag_returns_full_object(auth_client):
    """Get tag returns full object with all fields"""

    with allure.step("Create a tag"):
        created = auth_client.post('/api/tags', data={
            "name": "test-tag",
            "color": "#ff5733"
        })
        tag_id = created['id']

    with allure.step("Retrieve tag by ID"):
        response = auth_client.get(f'/api/tags/{tag_id}')

    with allure.step("Verify all fields present"):
        assert response['id'] == tag_id
        assert response['user_id']
        assert response['name'] == "test-tag"
        assert response['color'] == "#ff5733"
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Tags')
@allure.story('Get Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_tag(auth_client):
    """Get nonexistent tag returns 404"""

    with allure.step("Attempt to retrieve non-existent tag"):
        response = auth_client.get('/api/tags/999999', handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Tags')
@allure.story('Get Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_tag(auth_client, secondary_auth_client):
    """Get another user's tag returns 404"""

    with allure.step("Secondary user creates tag"):
        secondary_tag = secondary_auth_client.post('/api/tags', data={
            "name": "secondary-tag"
        })
        secondary_tag_id = secondary_tag['id']

    with allure.step("Primary user attempts to retrieve secondary user's tag"):
        response = auth_client.get(f'/api/tags/{secondary_tag_id}', handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404