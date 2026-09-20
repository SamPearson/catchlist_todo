import pytest
import allure
from test_utils.data_factories.entity_factory import get_catchlist, update_catchlist


@allure.feature('Catchlist')
@allure.story('Update Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_catch_list_overwrites_previous_content(auth_client):
    """PUT replaces the entire blob"""

    with allure.step("Save initial content"):
        update_catchlist(auth_client, "thought one")

    with allure.step("Save replacement content"):
        replaced = update_catchlist(auth_client, "completely different thought")

    with allure.step("Verify content was fully replaced"):
        assert replaced['content'] == "completely different thought"

    with allure.step("Verify no old content remains"):
        fetched = get_catchlist(auth_client)
        assert fetched['content'] == "completely different thought"


@allure.feature('Catchlist')
@allure.story('Update Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_catch_list_preserves_newlines(auth_client):
    """Multi-line blobs round-trip with newlines intact"""

    blob = "line one\nline two\n\nline three"
    saved = update_catchlist(auth_client, blob)

    with allure.step("Verify newlines preserved"):
        assert saved['content'] == blob
        assert "\n" in saved['content']


@allure.feature('Catchlist')
@allure.story('Update Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_catch_list_with_empty_content(auth_client):
    """PUT with empty string clears the catch list (the 'empty it out' workflow)"""

    with allure.step("Save some content first"):
        update_catchlist(auth_client, "stuff to clear out")

    with allure.step("Save empty content"):
        cleared = update_catchlist(auth_client, "")

    with allure.step("Verify catch list is empty"):
        assert cleared['content'] == ""


@allure.feature('Catchlist')
@allure.story('Update Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_catch_list_requires_content_field(auth_client):
    """PUT without a content field is a client error"""

    with allure.step("PUT without content field"):
        response = auth_client.put('/api/catchlist', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        assert "content" in response.json['error']


@allure.feature('Catchlist')
@allure.story('Update Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_catch_list_rejects_oversized_content(auth_client):
    """Content longer than the maximum length is rejected"""

    oversize = "x" * 100001

    with allure.step("PUT with oversized content"):
        response = auth_client.put(
            '/api/catchlist', data={"content": oversize}, handle_response=False
        )

    with allure.step("Verify 422 error"):
        assert response.status_code == 422
        assert "error" in response.json