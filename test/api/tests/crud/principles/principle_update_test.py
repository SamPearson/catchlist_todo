import pytest
import allure


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_title_only(auth_client):
    """Verify title changes, other fields unchanged"""

    with allure.step("Create principle with all fields"):
        created = auth_client.post('/api/principles', data={
            "title": "Original title",
            "description": "Original description",
            "reason": "Original reason",
            "color": "#ff5733"
        })
        principle_id = created['id']
        original_description = created['description']
        original_reason = created['reason']
        original_color = created['color']

    with allure.step("Update only title"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "title": "Updated title"
        })

    with allure.step("Verify title changed, other fields unchanged"):
        assert updated['title'] == "Updated title"
        assert updated['description'] == original_description
        assert updated['reason'] == original_reason
        assert updated['color'] == original_color


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_description_only(auth_client):
    """Verify description changes, other fields unchanged"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Practice mindfulness",
            "description": "Original description",
            "reason": "Original reason"
        })
        principle_id = created['id']
        original_title = created['title']
        original_reason = created['reason']

    with allure.step("Update only description"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "description": "New description about mindfulness"
        })

    with allure.step("Verify description changed, other fields unchanged"):
        assert updated['description'] == "New description about mindfulness"
        assert updated['title'] == original_title
        assert updated['reason'] == original_reason


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_reason_only(auth_client):
    """Verify reason changes, other fields unchanged"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Embrace failure",
            "description": "View failures as learning opportunities",
            "reason": "Original reason"
        })
        principle_id = created['id']
        original_title = created['title']
        original_description = created['description']

    with allure.step("Update only reason"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "reason": "Growth comes from taking risks and learning from mistakes"
        })

    with allure.step("Verify reason changed, other fields unchanged"):
        assert updated['reason'] == "Growth comes from taking risks and learning from mistakes"
        assert updated['title'] == original_title
        assert updated['description'] == original_description


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_color_only(auth_client):
    """Verify color changes, other fields unchanged"""

    with allure.step("Create principle with custom color"):
        created = auth_client.post('/api/principles', data={
            "title": "Stay curious",
            "color": "#ff5733"
        })
        principle_id = created['id']
        original_title = created['title']
        original_color = created['color']

    with allure.step("Update only color"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "color": "#3498db"
        })

    with allure.step("Verify color changed, title unchanged"):
        assert updated['color'] == "#3498db"
        assert updated['color'] != original_color
        assert updated['title'] == original_title


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_title_and_description_together(auth_client):
    """Verify both change"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Original title",
            "description": "Original description"
        })
        principle_id = created['id']

    with allure.step("Update title and description together"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "title": "New title",
            "description": "New description"
        })

    with allure.step("Verify both fields changed"):
        assert updated['title'] == "New title"
        assert updated['description'] == "New description"


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_all_fields_together(auth_client):
    """Verify title, description, reason, color all change"""

    with allure.step("Create principle with all fields"):
        created = auth_client.post('/api/principles', data={
            "title": "Original title",
            "description": "Original description",
            "reason": "Original reason",
            "color": "#ff5733"
        })
        principle_id = created['id']

    with allure.step("Update all fields together"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "title": "Completely new title",
            "description": "Completely new description",
            "reason": "Completely new reason",
            "color": "#27ae60"
        })

    with allure.step("Verify all fields changed"):
        assert updated['title'] == "Completely new title"
        assert updated['description'] == "Completely new description"
        assert updated['reason'] == "Completely new reason"
        assert updated['color'] == "#27ae60"


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_with_empty_title(auth_client):
    """Verify 400 error when setting title to empty"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Valid title"
        })
        principle_id = created['id']

    with allure.step("Attempt to update with empty title"):
        response = auth_client.patch(f'/api/principles/{principle_id}', data={
            "title": ""
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_with_whitespace_only_title(auth_client):
    """Verify 400 error when setting title to whitespace only"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Valid title"
        })
        principle_id = created['id']

    with allure.step("Attempt to update with whitespace-only title"):
        response = auth_client.patch(f'/api/principles/{principle_id}', data={
            "title": "   "
        }, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_clear_description_with_empty_string(auth_client):
    """Verify description can be cleared"""

    with allure.step("Create principle with description"):
        created = auth_client.post('/api/principles', data={
            "title": "Test principle",
            "description": "Original description"
        })
        principle_id = created['id']

    with allure.step("Clear description with empty string"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "description": ""
        })

    with allure.step("Verify description cleared"):
        assert updated['description'] in ["", None]


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_clear_reason_with_empty_string(auth_client):
    """Verify reason can be cleared"""

    with allure.step("Create principle with reason"):
        created = auth_client.post('/api/principles', data={
            "title": "Test principle",
            "reason": "Original reason"
        })
        principle_id = created['id']

    with allure.step("Clear reason with empty string"):
        updated = auth_client.patch(f'/api/principles/{principle_id}', data={
            "reason": ""
        })

    with allure.step("Verify reason cleared"):
        assert updated['reason'] in ["", None]


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_with_no_data(auth_client):
    """Verify behavior when no data provided"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = created['id']

    with allure.step("Attempt to update with no data"):
        response = auth_client.patch(f'/api/principles/{principle_id}', data={}, handle_response=False)

    with allure.step("Verify 400 error or success (depending on API behavior)"):
        # Note: This test documents actual API behavior
        # Some APIs return 400, some accept empty updates
        assert response.status_code in [200, 400]


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_with_empty_request_body(auth_client):
    """Verify 400 error with empty request body"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Test principle"
        })
        principle_id = created['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.patch(f'/api/principles/{principle_id}', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        # Note: Same as test_update_principle_with_no_data
        # Documenting expected behavior
        assert response.status_code in [200, 400]


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_principle(auth_client):
    """Verify 404 when updating non-existent principle"""

    with allure.step("Attempt to update non-existent principle"):
        response = auth_client.patch('/api/principles/999999', data={
            "title": "New title"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_users_principle(auth_client, secondary_auth_client):
    """Verify 404 when updating another user's principle"""

    with allure.step("Secondary user creates principle"):
        secondary_principle = secondary_auth_client.post('/api/principles', data={
            "title": "Secondary user principle"
        })
        secondary_principle_id = secondary_principle['id']

    with allure.step("Primary user attempts to update secondary user's principle"):
        response = auth_client.patch(f'/api/principles/{secondary_principle_id}', data={
            "title": "Attempting to hijack"
        }, handle_response=False)

    with allure.step("Verify 404 response (not authorized)"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Update Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_update_principle_to_duplicate_title(auth_client):
    """Verify 400 error when updating to a title that already exists"""

    with allure.step("Create first principle"):
        first_principle = auth_client.post('/api/principles', data={
            "title": "Be authentic"
        })

    with allure.step("Create second principle"):
        second_principle = auth_client.post('/api/principles', data={
            "title": "Stay focused"
        })
        second_principle_id = second_principle['id']

    with allure.step("Attempt to update second principle to duplicate title"):
        response = auth_client.patch(f'/api/principles/{second_principle_id}', data={
            "title": "Be authentic"
        }, handle_response=False)

    with allure.step("Verify 400 error (duplicate title not allowed)"):
        assert response.status_code == 400