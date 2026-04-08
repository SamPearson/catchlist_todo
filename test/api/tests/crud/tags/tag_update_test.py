import pytest
import allure


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_tag_name_only(auth_client):
    """Update tag name only, verify color unchanged"""

    with allure.step("Create tag with name and color"):
        created = auth_client.post('/api/tags', data={
            "name": "original-name",
            "color": "#ff0000"
        })
        tag_id = created['id']
        original_color = created['color']

    with allure.step("Update only the name"):
        payload = {
            "name": "updated-name"
        }
        response = auth_client.patch(f'/api/tags/{tag_id}', data=payload)

    with allure.step("Verify name changed and color unchanged"):
        assert response['id'] == tag_id
        assert response['name'] == "updated-name"
        assert response['color'] == original_color


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_tag_color_only(auth_client):
    """Update tag color only, verify name unchanged"""

    with allure.step("Create tag with name and color"):
        created = auth_client.post('/api/tags', data={
            "name": "test-tag",
            "color": "#ff0000"
        })
        tag_id = created['id']
        original_name = created['name']

    with allure.step("Update only the color"):
        payload = {
            "color": "#00ff00"
        }
        response = auth_client.patch(f'/api/tags/{tag_id}', data=payload)

    with allure.step("Verify color changed and name unchanged"):
        assert response['id'] == tag_id
        assert response['name'] == original_name
        assert response['color'] == "#00ff00"


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_tag_name_and_color_together(auth_client):
    """Update tag name and color together"""

    with allure.step("Create tag"):
        created = auth_client.post('/api/tags', data={
            "name": "original",
            "color": "#ff0000"
        })
        tag_id = created['id']

    with allure.step("Update both name and color"):
        payload = {
            "name": "updated",
            "color": "#0000ff"
        }
        response = auth_client.patch(f'/api/tags/{tag_id}', data=payload)

    with allure.step("Verify both fields changed"):
        assert response['id'] == tag_id
        assert response['name'] == "updated"
        assert response['color'] == "#0000ff"


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_tag_with_empty_name(auth_client):
    """Update tag with empty name returns 400"""

    with allure.step("Create tag"):
        created = auth_client.post('/api/tags', data={"name": "test-tag"})
        tag_id = created['id']

    with allure.step("Attempt to update with empty name"):
        payload = {
            "name": ""
        }
        response = auth_client.patch(f'/api/tags/{tag_id}', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_tag_with_whitespace_only_name(auth_client):
    """Update tag with whitespace-only name returns 400"""

    with allure.step("Create tag"):
        created = auth_client.post('/api/tags', data={"name": "test-tag"})
        tag_id = created['id']

    with allure.step("Attempt to update with whitespace-only name"):
        payload = {
            "name": "   \n\t   "
        }
        response = auth_client.patch(f'/api/tags/{tag_id}', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_tag_with_no_data(auth_client):
    """Update tag with no data returns 400"""

    with allure.step("Create tag"):
        created = auth_client.post('/api/tags', data={"name": "test-tag"})
        tag_id = created['id']

    with allure.step("Attempt to update with no data"):
        response = auth_client.patch(f'/api/tags/{tag_id}', data=None, handle_response=False)

    with allure.step("Verify 415 error"):
        assert response.status_code == 415


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_tag_with_empty_request_body(auth_client):
    """Update tag with empty request body returns 400"""

    with allure.step("Create tag"):
        created = auth_client.post('/api/tags', data={"name": "test-tag"})
        tag_id = created['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.patch(f'/api/tags/{tag_id}', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_tag(auth_client):
    """Update nonexistent tag returns 404"""

    with allure.step("Attempt to update non-existent tag"):
        payload = {
            "name": "updated-name"
        }
        response = auth_client.patch('/api/tags/999999', data=payload, handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Tags')
@allure.story('Update Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_users_tag(auth_client, secondary_auth_client):
    """Update another user's tag returns 404"""

    with allure.step("Secondary user creates tag"):
        secondary_tag = secondary_auth_client.post('/api/tags', data={
            "name": "secondary-tag"
        })
        secondary_tag_id = secondary_tag['id']

    with allure.step("Primary user attempts to update secondary user's tag"):
        payload = {
            "name": "hacked-name"
        }
        response = auth_client.patch(f'/api/tags/{secondary_tag_id}',
                                    data=payload,
                                    handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404