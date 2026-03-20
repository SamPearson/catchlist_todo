import pytest
import allure


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_title(auth_client):
    """Update project title"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Original title"
        })
        project_id = created['id']

    with allure.step("Update project title"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "title": "Updated title"
        })

    with allure.step("Verify title was updated"):
        assert updated['title'] == "Updated title"
        assert updated['id'] == project_id
        assert updated['created_at'] == created['created_at']
        assert updated['updated_at'] >= created['updated_at']


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_description(auth_client):
    """Update project description"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Update project description"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "description": "New description"
        })

    with allure.step("Verify description was updated"):
        assert updated['description'] == "New description"
        assert updated['id'] == project_id


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_win_condition(auth_client):
    """Update project win_condition"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Update project win_condition"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "win_condition": "Clear completion criteria"
        })

    with allure.step("Verify win_condition was updated"):
        assert updated['win_condition'] == "Clear completion criteria"
        assert updated['id'] == project_id


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_reason(auth_client):
    """Update project reason"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Update project reason"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "reason": "Why this matters"
        })

    with allure.step("Verify reason was updated"):
        assert updated['reason'] == "Why this matters"
        assert updated['id'] == project_id


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_next_step(auth_client):
    """Update project next_step"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Update project next_step"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "next_step": "Call the client"
        })

    with allure.step("Verify next_step was updated"):
        assert updated['next_step'] == "Call the client"
        assert updated['id'] == project_id


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_multiple_fields_together(auth_client):
    """Update multiple fields at once"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Original title"
        })
        project_id = created['id']

    with allure.step("Update multiple fields"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "title": "New title",
            "description": "New description",
            "next_step": "New step"
        })

    with allure.step("Verify all fields were updated"):
        assert updated['title'] == "New title"
        assert updated['description'] == "New description"
        assert updated['next_step'] == "New step"
        assert updated['id'] == project_id


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_with_empty_title(auth_client):
    """Update project with empty title returns 400"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Original title"
        })
        project_id = created['id']

    with allure.step("Attempt to update with empty title"):
        response = auth_client.put(f'/api/projects/{project_id}', {
            "title": ""
        }, handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_with_no_data(auth_client):
    """Update project with no data returns 400"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.put(f'/api/projects/{project_id}', {},
                                    handle_response=False)

    with allure.step("Verify 400 response"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_with_disallowed_field_status(auth_client):
    """Update project with disallowed field 'status' returns 400"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Attempt to update status via PUT"):
        response = auth_client.put(f'/api/projects/{project_id}', {
            "status": "waiting"
        }, handle_response=False)

    with allure.step("Verify 400 response with error about using dedicated endpoint"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_with_disallowed_field_active(auth_client):
    """Update project with disallowed field 'active' returns 400"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Attempt to update active via PUT"):
        response = auth_client.put(f'/api/projects/{project_id}', {
            "active": False
        }, handle_response=False)

    with allure.step("Verify 400 response with error about using dedicated endpoint"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_with_disallowed_field_completed(auth_client):
    """Update project with disallowed field 'completed' returns 400"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Attempt to update completed via PUT"):
        response = auth_client.put(f'/api/projects/{project_id}', {
            "completed": True
        }, handle_response=False)

    with allure.step("Verify 400 response with error about using dedicated endpoint"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_project_with_disallowed_field_completed_at(auth_client):
    """Update project with disallowed field 'completed_at' returns 400"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']

    with allure.step("Attempt to update completed_at via PUT"):
        response = auth_client.put(f'/api/projects/{project_id}', {
            "completed_at": "2026-03-19T12:00:00"
        }, handle_response=False)

    with allure.step("Verify 400 response with error about using dedicated endpoint"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_project(auth_client):
    """Update nonexistent project returns 404"""
    with allure.step("Attempt to update nonexistent project"):
        response = auth_client.put('/api/projects/999999', {
            "title": "Updated"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Update Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_users_project(auth_client, secondary_auth_client):
    """Update another user's project returns 404"""
    with allure.step("Create project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project"
        })
        project_id = project['id']

    with allure.step("Attempt to update as first user"):
        response = auth_client.put(f'/api/projects/{project_id}', {
            "title": "Hacked title"
        }, handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404