import pytest
import allure


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_all_fields(auth_client):
    """Create tag with name and color"""

    with allure.step("Create tag with all fields"):
        payload = {
            "name": "urgent",
            "color": "#ff0000"
        }
        response = auth_client.post('/api/tags', data=payload)

    with allure.step("Verify all fields returned correctly"):
        assert response['id']
        assert response['name'] == "urgent"
        assert response['color'] == "#ff0000"
        assert response['user_id']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_verifies_defaults(auth_client):
    """Verify color defaults to #6c757d (gray) when not specified"""

    with allure.step("Create tag without color"):
        payload = {
            "name": "work"
        }
        response = auth_client.post('/api/tags', data=payload)

    with allure.step("Verify default color applied"):
        assert response['id']
        assert response['name'] == "work"
        assert response['color'] == "#6c757d", \
            f"Expected default color #6c757d, got {response['color']}"


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_custom_color(auth_client):
    """Create tag with custom color"""

    with allure.step("Create tag with custom color"):
        payload = {
            "name": "health",
            "color": "#00ff00"
        }
        response = auth_client.post('/api/tags', data=payload)

    with allure.step("Verify custom color set correctly"):
        assert response['id']
        assert response['name'] == "health"
        assert response['color'] == "#00ff00"


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_without_name(auth_client):
    """Create tag without name returns 400"""

    with allure.step("Attempt to create tag without name"):
        payload = {
            "color": "#ff0000"
        }
        response = auth_client.post('/api/tags', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_empty_name(auth_client):
    """Create tag with empty name returns 400"""

    with allure.step("Attempt to create tag with empty name"):
        payload = {
            "name": ""
        }
        response = auth_client.post('/api/tags', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_whitespace_only_name(auth_client):
    """Create tag with whitespace-only name returns 400"""

    with allure.step("Attempt to create tag with whitespace-only name"):
        payload = {
            "name": "   \n\t   "
        }
        response = auth_client.post('/api/tags', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_name_exactly_50_chars(auth_client):
    """Create tag with name exactly 50 chars (boundary)"""

    with allure.step("Create tag with 50-character name"):
        name_50_chars = "a" * 50
        payload = {
            "name": name_50_chars
        }
        response = auth_client.post('/api/tags', data=payload)

    with allure.step("Verify tag created successfully"):
        assert response['id']
        assert response['name'] == name_50_chars
        assert len(response['name']) == 50


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_name_over_50_chars(auth_client):
    """Create tag with name over 50 chars returns 400 (boundary)"""

    with allure.step("Attempt to create tag with 51-character name"):
        name_51_chars = "a" * 51
        payload = {
            "name": name_51_chars
        }
        response = auth_client.post('/api/tags', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_color_exactly_6_chars(auth_client):
    """Create tag with color exactly 6 chars (boundary)"""

    with allure.step("Create tag with 6-character color"):
        color_6_chars = "#123456"
        payload = {
            "name": "color-test",
            "color": color_6_chars
        }
        response = auth_client.post('/api/tags', data=payload)

    with allure.step("Verify tag created successfully"):
        assert response['id']
        assert response['color'] == color_6_chars
        assert len(response['color']) == 7 # including hashmark


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_color_missing_hashmark(auth_client):
    """Create tag with color exactly 6 chars and no hashmark"""

    with allure.step("Create tag with 6-character color without hashmark"):
        color_without_hash = "123456"
        color_with_hash = f'#{color_without_hash}'

        payload = {
            "name": "color-test",
            "color": color_without_hash
        }
        response = auth_client.post('/api/tags', data=payload)

    with allure.step("Verify tag created successfully"):
        assert response['id']
        assert response['color'] == color_with_hash
        assert len(response['color']) == 7 # including hashmark


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_color_over_6_chars(auth_client):
    """Create tag with color over 6 chars returns 400 (boundary)"""

    with allure.step("Attempt to create tag with 7-character color"):
        color_7_chars = "#1234567"  # 7
        payload = {
            "name": "color-test",
            "color": color_7_chars
        }
        response = auth_client.post('/api/tags', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_tag_with_empty_request_body(auth_client):
    """Create tag with empty request body returns 400"""

    with allure.step("Attempt to create tag with empty body"):
        response = auth_client.post('/api/tags', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Tags')
@allure.story('Create Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_duplicate_tag_name(auth_client):
    """Create duplicate tag name is allowed (tags can have same name)"""

    with allure.step("Create first tag"):
        initial_response = auth_client.post('/api/tags', data={"name": "duplicate"})

    with allure.step("Create second tag with same name"):
        duplicate_response = auth_client.post('/api/tags', data={"name": "duplicate"},
                                              handle_response=False)

    with allure.step("Verify duplicate cannot be created"):
        assert duplicate_response.status_code == 400