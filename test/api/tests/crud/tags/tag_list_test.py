import pytest
import allure


@allure.feature('Tags')
@allure.story('List Tags')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_list_tags_returns_empty_array(auth_client):
    """New user with no tags gets empty array"""

    with allure.step("List tags for new user"):
        response = auth_client.get('/api/tags')

    with allure.step("Verify empty array returned"):
        assert isinstance(response.json, list)
        assert len(response.json) == 0


@allure.feature('Tags')
@allure.story('List Tags')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_list_tags_only_returns_users_own_tags(auth_client, secondary_auth_client):
    """Create tags for two different users, verify isolation"""

    with allure.step("Primary user creates tags"):
        primary_tag1 = auth_client.post('/api/tags', data={"name": "primary-work"})
        primary_tag2 = auth_client.post('/api/tags', data={"name": "primary-home"})

    with allure.step("Secondary user creates tags"):
        secondary_tag1 = secondary_auth_client.post('/api/tags', data={"name": "secondary-urgent"})
        secondary_tag2 = secondary_auth_client.post('/api/tags', data={"name": "secondary-health"})

    with allure.step("Primary user lists tags"):
        primary_tags = auth_client.get('/api/tags')

    with allure.step("Verify primary user only sees their own tags"):
        primary_ids = [tag['id'] for tag in primary_tags.json]
        assert primary_tag1['id'] in primary_ids
        assert primary_tag2['id'] in primary_ids
        assert secondary_tag1['id'] not in primary_ids
        assert secondary_tag2['id'] not in primary_ids
        assert len(primary_tags.json) == 2

    with allure.step("Secondary user lists tags"):
        secondary_tags = secondary_auth_client.get('/api/tags')

    with allure.step("Verify secondary user only sees their own tags"):
        secondary_ids = [tag['id'] for tag in secondary_tags.json]
        assert secondary_tag1['id'] in secondary_ids
        assert secondary_tag2['id'] in secondary_ids
        assert primary_tag1['id'] not in secondary_ids
        assert primary_tag2['id'] not in secondary_ids
        assert len(secondary_tags.json) == 2


@allure.feature('Tags')
@allure.story('List Tags')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_list_tags_returns_all_tags(auth_client):
    """Create 5 tags, verify all returned (no filtering)"""

    with allure.step("Create 5 tags"):
        tag_names = ["work", "home", "urgent", "health", "learning"]
        created_tags = []
        for name in tag_names:
            tag = auth_client.post('/api/tags', data={"name": name})
            created_tags.append(tag)

    with allure.step("List all tags"):
        response = auth_client.get('/api/tags')

    with allure.step("Verify all 5 tags returned"):
        assert isinstance(response.json, list)
        assert len(response.json) == 5

        returned_ids = [tag['id'] for tag in response.json]
        for created_tag in created_tags:
            assert created_tag['id'] in returned_ids, \
                f"Tag {created_tag['id']} ({created_tag['name']}) not found in list"