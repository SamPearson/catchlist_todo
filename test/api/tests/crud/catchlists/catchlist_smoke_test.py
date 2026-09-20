import pytest
import allure
from test_utils.data_factories.entity_factory import get_catchlist, update_catchlist


@allure.feature('Catchlist')
@allure.story('Get Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_empty_catchlist_for_new_user(auth_client):
    """A brand-new user gets an empty catch list without having to create it first"""

    with allure.step("Fetch catch list for a fresh user"):
        response = auth_client.get('/api/catchlist', handle_response=False)

    with allure.step("Verify 200 with empty content"):
        assert response.status_code == 200
        body = response.json
        assert body['content'] == ""
        assert body['user_id']
        assert body['created_at']
        assert body['updated_at']


@allure.feature('Catchlist')
@allure.story('Update Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_save_and_retrieve_catch_list(auth_client):
    """Saving a blob then retrieving it returns the exact same content"""

    blob = "fix the leaky roof\ncall dentist re: Saturday\ngift idea: cast iron skillet"

    with allure.step("Save catch list content"):
        saved = update_catchlist(auth_client, blob)

    with allure.step("Verify saved content persists"):
        assert saved['content'] == blob
        assert saved['id']

    with allure.step("Retrieve catch list"):
        fetched = get_catchlist(auth_client)

    with allure.step("Verify retrieved content matches what was saved"):
        assert fetched['id'] == saved['id']
        assert fetched['content'] == blob