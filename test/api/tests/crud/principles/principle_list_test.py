import pytest
import allure


@allure.feature('Principles')
@allure.story('List Principles')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_list_principles_returns_empty_array(auth_client):
    """New user with no principles gets empty array"""

    with allure.step("List principles for new user"):
        response = auth_client.get('/api/principles')

    with allure.step("Verify empty array returned"):
        assert isinstance(response.json, list)
        assert len(response.json) == 0


@allure.feature('Principles')
@allure.story('List Principles')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_list_principles_only_returns_own_principles(auth_client, secondary_auth_client):
    """Create principles for two different users, verify isolation"""

    with allure.step("Primary user creates principles"):
        primary_principle_1 = auth_client.post('/api/principles', data={
            "title": "Primary user principle 1"
        })
        primary_principle_2 = auth_client.post('/api/principles', data={
            "title": "Primary user principle 2"
        })

    with allure.step("Secondary user creates principles"):
        secondary_principle_1 = secondary_auth_client.post('/api/principles', data={
            "title": "Secondary user principle 1"
        })
        secondary_principle_2 = secondary_auth_client.post('/api/principles', data={
            "title": "Secondary user principle 2"
        })

    with allure.step("Primary user lists principles"):
        primary_list = auth_client.get('/api/principles')
        primary_list_ids = [p['id'] for p in primary_list.json]

    with allure.step("Verify primary user only sees own principles"):
        assert primary_principle_1['id'] in primary_list_ids
        assert primary_principle_2['id'] in primary_list_ids
        assert secondary_principle_1['id'] not in primary_list_ids
        assert secondary_principle_2['id'] not in primary_list_ids

    with allure.step("Secondary user lists principles"):
        secondary_list = secondary_auth_client.get('/api/principles')
        secondary_list_ids = [p['id'] for p in secondary_list.json]

    with allure.step("Verify secondary user only sees own principles"):
        assert secondary_principle_1['id'] in secondary_list_ids
        assert secondary_principle_2['id'] in secondary_list_ids
        assert primary_principle_1['id'] not in secondary_list_ids
        assert primary_principle_2['id'] not in secondary_list_ids


@allure.feature('Principles')
@allure.story('List Principles')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_list_principles_returns_all_principles(auth_client):
    """Create 5 principles, verify all returned (no filtering)"""

    with allure.step("Create 5 principles"):
        created_principles = []
        for i in range(1, 6):
            principle = auth_client.post('/api/principles', data={
                "title": f"Test principle {i}"
            })
            created_principles.append(principle['id'])

    with allure.step("List all principles"):
        response = auth_client.get('/api/principles')
        returned_ids = [p['id'] for p in response.json]

    with allure.step("Verify all 5 principles returned"):
        assert len(response.json) == 5, f"Expected 5 principles, got {len(response.json)}"
        for principle_id in created_principles:
            assert principle_id in returned_ids, \
                f"Principle {principle_id} not found in returned list"