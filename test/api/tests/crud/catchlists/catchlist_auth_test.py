import pytest
import allure


@allure.feature('Catchlist')
@allure.story('Authentication')
@pytest.mark.catchlists
@pytest.mark.crud
@pytest.mark.auth
@allure.severity(allure.severity_level.CRITICAL)
def test_get_catch_list_requires_auth(unauthenticated_client):
    """GET /api/catchlist without a token is rejected"""

    with allure.step("GET without auth token"):
        response = unauthenticated_client.get('/api/catchlist', handle_response=False)

    with allure.step("Verify 422 from missing auth header"):
        assert response.status_code == 422


@allure.feature('Catchlist')
@allure.story('Authentication')
@pytest.mark.catchlists
@pytest.mark.crud
@pytest.mark.auth
@allure.severity(allure.severity_level.CRITICAL)
def test_update_catch_list_requires_auth(unauthenticated_client):
    """PUT /api/catchlist without a token is rejected"""

    with allure.step("PUT without auth token"):
        response = unauthenticated_client.put(
            '/api/catchlist', data={"content": "anything"}, handle_response=False
        )

    with allure.step("Verify 422 from missing auth header"):
        assert response.status_code == 422