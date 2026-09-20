import pytest
import allure
from test_utils.data_factories.entity_factory import get_catchlist, update_catchlist


@allure.feature('Catchlist')
@allure.story('Per-User Isolation')
@pytest.mark.catchlists
@pytest.mark.crud
@pytest.mark.multi_user
@allure.severity(allure.severity_level.CRITICAL)
def test_catch_list_is_isolated_per_user(auth_client, secondary_auth_client):
    """Each user's catch list is a separate, privately-owned blob"""

    with allure.step("Primary user saves content"):
        update_catchlist(auth_client, "primary user's private thoughts")

    with allure.step("Secondary user retrieves their own (empty) catch list"):
        secondary = get_catchlist(secondary_auth_client)
        assert secondary['content'] == ""

    with allure.step("Secondary user saves their own content"):
        update_catchlist(secondary_auth_client, "secondary user's private thoughts")

    with allure.step("Verify isolation holds in both directions"):
        primary_again = get_catchlist(auth_client)
        secondary_again = get_catchlist(secondary_auth_client)
        assert primary_again['content'] == "primary user's private thoughts"
        assert secondary_again['content'] == "secondary user's private thoughts"


@allure.feature('Catchlist')
@allure.story('Per-User Isolation')
@pytest.mark.catchlists
@pytest.mark.crud
@pytest.mark.multi_user
@allure.severity(allure.severity_level.CRITICAL)
def test_catch_list_rows_are_distinct_per_user(auth_client, secondary_auth_client):
    """Distinct users get distinct catch list rows"""

    with allure.step("Both users save content"):
        primary = update_catchlist(auth_client, "a")
        secondary = update_catchlist(secondary_auth_client, "b")

    with allure.step("Verify rows are distinct"):
        assert primary['id'] != secondary['id']
        assert primary['user_id'] != secondary['user_id']