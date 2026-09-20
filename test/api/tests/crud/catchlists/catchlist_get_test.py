import pytest
import allure
from test_utils.data_factories.entity_factory import get_catchlist, update_catchlist


@allure.feature('Catchlist')
@allure.story('Get Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_catch_list_does_not_duplicate_rows(auth_client):
    """Repeated GETs return the same singleton rather than creating new rows"""

    with allure.step("Fetch catch list twice"):
        first = get_catchlist(auth_client)
        second = get_catchlist(auth_client)

    with allure.step("Verify same catch list is returned"):
        assert first['id'] == second['id']
        assert first['content'] == second['content']


@allure.feature('Catchlist')
@allure.story('Get Catch List')
@pytest.mark.catchlists
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_catch_list_reflects_saved_content(auth_client):
    """GET returns the content saved by an earlier PUT"""

    with allure.step("Save some content"):
        update_catchlist(auth_client, "capture: vacation itinerary")

    with allure.step("Fetch catch list and verify content"):
        fetched = get_catchlist(auth_client)
        assert fetched['content'] == "capture: vacation itinerary"