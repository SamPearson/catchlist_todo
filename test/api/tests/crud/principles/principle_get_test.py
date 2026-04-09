import pytest
import allure


@allure.feature('Principles')
@allure.story('Get Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_principle_returns_full_object(auth_client):
    """Verify all fields present (id, user_id, title, description, reason, color, created_at, updated_at)"""

    with allure.step("Create principle with all fields"):
        created = auth_client.post('/api/principles', data={
            "title": "Practice empathy",
            "description": "Try to understand others' perspectives and feelings before judging",
            "reason": "Empathy builds stronger relationships and helps me be a better person",
            "color": "#9b59b6"
        })
        principle_id = created['id']

    with allure.step("Retrieve principle by ID"):
        response = auth_client.get(f'/api/principles/{principle_id}')

    with allure.step("Verify all fields present and correct"):
        assert response['id'] == principle_id
        assert response['user_id']
        assert response['title'] == "Practice empathy"
        assert response['description'] == "Try to understand others' perspectives and feelings before judging"
        assert response['reason'] == "Empathy builds stronger relationships and helps me be a better person"
        assert response['color'] == "#9b59b6"
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Principles')
@allure.story('Get Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_principle(auth_client):
    """Verify 404 for non-existent principle"""

    with allure.step("Request non-existent principle"):
        response = auth_client.get('/api/principles/999999', handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Get Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_principle(auth_client, secondary_auth_client):
    """Verify 404 when accessing another user's principle"""

    with allure.step("Secondary user creates principle"):
        secondary_principle = secondary_auth_client.post('/api/principles', data={
            "title": "Secondary user principle"
        })
        secondary_principle_id = secondary_principle['id']

    with allure.step("Primary user attempts to access secondary user's principle"):
        response = auth_client.get(f'/api/principles/{secondary_principle_id}', handle_response=False)

    with allure.step("Verify 404 response (not authorized to access)"):
        assert response.status_code == 404