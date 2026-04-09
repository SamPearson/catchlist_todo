import pytest
import allure



@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_all_fields(auth_client):
    """Create principle with title, description, reason, and color"""

    with allure.step("Create principle with all fields"):
        payload = {
            "title": "Be dependable",
            "description": "Show up on time, follow through on commitments, be someone others can count on",
            "reason": "I want to be known as someone trustworthy and reliable",
            "color": "#4a90e2"
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify all fields set correctly"):
        assert response['id']
        assert response['title'] == "Be dependable"
        assert response['description'] == "Show up on time, follow through on commitments, be someone others can count on"
        assert response['reason'] == "I want to be known as someone trustworthy and reliable"
        assert response['color'] == "#4a90e2"
        assert response['user_id']
        assert response['created_at']
        assert response['updated_at']


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_verifies_defaults(auth_client):
    """Verify color defaults to #ffd700 (gold) when not specified"""

    with allure.step("Create principle without specifying color"):
        payload = {
            "title": "Prioritize health"
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify color defaults to gold"):
        assert response['color'] == "#ffd700"


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_custom_color(auth_client):
    """Verify color is set correctly"""

    with allure.step("Create principle with custom color"):
        payload = {
            "title": "Continuous learning",
            "color": "#ff5733"
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify custom color set"):
        assert response['color'] == "#ff5733"


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_description_only(auth_client):
    """Verify title + description works"""

    with allure.step("Create principle with title and description"):
        payload = {
            "title": "Practice gratitude",
            "description": "Take time each day to appreciate what I have and express thanks to others"
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify description stored correctly"):
        assert response['title'] == "Practice gratitude"
        assert response['description'] == "Take time each day to appreciate what I have and express thanks to others"
        assert response.get('reason') in [None, '']  # reason not provided


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_reason_only(auth_client):
    """Verify title + reason works"""

    with allure.step("Create principle with title and reason"):
        payload = {
            "title": "Financial independence",
            "reason": "I want freedom to choose work I'm passionate about without financial pressure"
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify reason stored correctly"):
        assert response['title'] == "Financial independence"
        assert response['reason'] == "I want freedom to choose work I'm passionate about without financial pressure"
        assert response.get('description') in [None, '']  # description not provided


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_description_and_reason(auth_client):
    """Verify both fields stored"""

    with allure.step("Create principle with description and reason"):
        payload = {
            "title": "Maintain work-life balance",
            "description": "Set boundaries between work and personal time, prioritize family and self-care",
            "reason": "Preventing burnout allows me to be more effective and present in all areas of life"
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify both description and reason stored"):
        assert response['title'] == "Maintain work-life balance"
        assert response['description'] == "Set boundaries between work and personal time, prioritize family and self-care"
        assert response['reason'] == "Preventing burnout allows me to be more effective and present in all areas of life"


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_without_title(auth_client):
    """Verify 400 error when title missing"""

    with allure.step("Attempt to create principle without title"):
        payload = {
            "description": "A principle without a title"
        }
        response = auth_client.post('/api/principles', data=payload, handle_response=False)


    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_empty_title(auth_client):
    """Verify 400 error when title is empty"""

    with allure.step("Attempt to create principle with empty title"):
        payload = {
            "title": ""
        }
        response = auth_client.post('/api/principles', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_whitespace_only_title(auth_client):
    """Verify 400 error when title is whitespace only"""

    with allure.step("Attempt to create principle with whitespace-only title"):
        payload = {
            "title": "   "
        }
        response = auth_client.post('/api/principles', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_title_exactly_50_chars(auth_client):
    """Verify success with title at boundary (50 chars)"""

    with allure.step("Create principle with title exactly 50 characters"):
        # Create exactly 50 character title
        title = "A" * 50
        payload = {
            "title": title
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify principle created successfully"):
        assert response['id']
        assert response['title'] == title
        assert len(response['title']) == 50


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_title_over_50_chars(auth_client):
    """Verify 400 error when title exceeds 50 chars"""

    with allure.step("Attempt to create principle with title over 50 characters"):
        # Create 51 character title
        title = "A" * 51
        payload = {
            "title": title
        }
        response = auth_client.post('/api/principles', data=payload, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_long_description(auth_client):
    """Verify text field accepts long content"""

    with allure.step("Create principle with long description"):
        # Create a long description (1000+ characters)
        long_description = "This is a very detailed description. " * 50
        payload = {
            "title": "Principle with long description",
            "description": long_description
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify long description stored correctly"):
        assert response['description'] == long_description
        assert len(response['description']) > 1000


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_long_reason(auth_client):
    """Verify text field accepts long content"""

    with allure.step("Create principle with long reason"):
        # Create a long reason (1000+ characters)
        long_reason = "This is why this principle is important to me. " * 50
        payload = {
            "title": "Principle with long reason",
            "reason": long_reason
        }
        response = auth_client.post('/api/principles', data=payload)

    with allure.step("Verify long reason stored correctly"):
        assert response['reason'] == long_reason
        assert len(response['reason']) > 1000


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_principle_with_empty_request_body(auth_client):
    """Verify 400 error with empty request body"""

    with allure.step("Attempt to create principle with empty body"):
        response = auth_client.post('/api/principles', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Create Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_create_duplicate_principle_title(auth_client):
    """Verify unallowed (principles cannot have same title)"""

    with allure.step("Create first principle"):
        first_principle = auth_client.post('/api/principles', data={
            "title": "Be authentic"
        })

    with allure.step("Create second principle with same title"):
        second_principle = auth_client.post('/api/principles', data={
            "title": "Be authentic"
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert second_principle.status_code == 400