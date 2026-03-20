import pytest
import allure


@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_project_with_next_step_win_condition_and_reason(auth_client):
    """Activating project with next_step, win_condition and reason sets active=true"""
    with allure.step("Create project with win_condition and reason"):
        project = auth_client.post('/api/projects', {
            "title": "Project to activate",
            "win_condition": "All tasks completed",
            "next_step": "Begin first task",
            "reason": "Important business goal"
        })
        project_id = project['id']

    with allure.step("Deactivate project first"):
        auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Activate the project"):
        activated = auth_client.patch(f'/api/projects/{project_id}/activate')

    with allure.step("Verify active is true"):
        assert activated['id'] == project_id
        assert activated['active'] is True


@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_project_missing_win_condition(auth_client):
    """Activate project missing win_condition returns 400 error"""
    with allure.step("Create project with reason but no win_condition"):
        project = auth_client.post('/api/projects', {
            "title": "Project without win_condition",
            "next_step": "Begin first task",
            "reason": "Important business goal"
        })
        project_id = project['id']

    with allure.step("Deactivate project first"):
        auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Attempt to activate project"):
        response = auth_client.patch(f'/api/projects/{project_id}/activate',
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400

@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_project_missing_next_step(auth_client):
    """Activate project missing next_step returns 400 error"""
    with allure.step("Create project with reason and win_condition but no next step"):
        project = auth_client.post('/api/projects', {
            "title": "Project without win_condition",
            "win_condition": "All tasks completed",
            "reason": "Important business goal"
        })
        project_id = project['id']

    with allure.step("Deactivate project first"):
        auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Attempt to activate project"):
        response = auth_client.patch(f'/api/projects/{project_id}/activate',
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400

@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_project_missing_reason(auth_client):
    """Activate project missing reason returns 400 error"""
    with allure.step("Create project with win_condition and next_step but no reason"):
        project = auth_client.post('/api/projects', {
            "title": "Project without reason",
            "win_condition": "All tasks completed",
            "next_step": "Begin first task"
        })
        project_id = project['id']

    with allure.step("Deactivate project first"):
        auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Attempt to activate project"):
        response = auth_client.patch(f'/api/projects/{project_id}/activate',
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_project_missing_next_step_win_condition_and_reason(auth_client):
    """Activate project missing next_step, win_condition and reason returns 400 error"""
    with allure.step("Create project without next_step, win_condition or reason"):
        project = auth_client.post('/api/projects', {
            "title": "Minimal project"
        })
        project_id = project['id']

    with allure.step("Deactivate project first"):
        auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Attempt to activate project"):
        response = auth_client.patch(f'/api/projects/{project_id}/activate',
                                     handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_already_active_project(auth_client):
    """Activate already active project is idempotent"""
    with allure.step("Create active project with required fields"):
        project = auth_client.post('/api/projects', {
            "title": "Already active project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        project_id = project['id']
        # Verify it starts active
        assert project['active'] is True

    with allure.step("Activate the already-active project"):
        activated = auth_client.patch(f'/api/projects/{project_id}/activate')

    with allure.step("Verify project remains active"):
        assert activated['active'] is True


@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_activate_nonexistent_project(auth_client):
    """Activate nonexistent project returns 404"""
    with allure.step("Attempt to activate nonexistent project"):
        response = auth_client.patch('/api/projects/999999/activate',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Activate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_activate_another_users_project(auth_client, secondary_auth_client):
    """Activate another user's project returns 404"""
    with allure.step("Create project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        project_id = project['id']

    with allure.step("Attempt to activate as first user"):
        response = auth_client.patch(f'/api/projects/{project_id}/activate',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify project is still in original state for second user"):
        get_response = secondary_auth_client.get(f'/api/projects/{project_id}')
        assert get_response['active'] is True


@allure.feature('Projects')
@allure.story('Deactivate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_project_sets_active_false(auth_client):
    """Deactivate project sets active=false"""
    with allure.step("Create active project"):
        project = auth_client.post('/api/projects', {
            "title": "Project to deactivate",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        project_id = project['id']
        assert project['active'] is True

    with allure.step("Deactivate the project"):
        deactivated = auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Verify active is false"):
        assert deactivated['id'] == project_id
        assert deactivated['active'] is False


@allure.feature('Projects')
@allure.story('Deactivate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_project_requires_no_validation(auth_client):
    """Deactivate project requires no validation (minimal project succeeds)"""
    with allure.step("Create minimal project without win_condition or reason"):
        project = auth_client.post('/api/projects', {
            "title": "Minimal project"
        })
        project_id = project['id']

    with allure.step("Deactivate the project"):
        deactivated = auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Verify deactivation succeeds"):
        assert deactivated['active'] is False


@allure.feature('Projects')
@allure.story('Deactivate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_already_inactive_project(auth_client):
    """Deactivate already inactive project is idempotent"""
    with allure.step("Create and deactivate project"):
        project = auth_client.post('/api/projects', {
            "title": "Inactive project"
        })
        project_id = project['id']
        auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Deactivate the already-inactive project"):
        deactivated = auth_client.patch(f'/api/projects/{project_id}/deactivate')

    with allure.step("Verify project remains inactive"):
        assert deactivated['active'] is False


@allure.feature('Projects')
@allure.story('Deactivate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_nonexistent_project(auth_client):
    """Deactivate nonexistent project returns 404"""
    with allure.step("Attempt to deactivate nonexistent project"):
        response = auth_client.patch('/api/projects/999999/deactivate',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Projects')
@allure.story('Deactivate Project')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.update
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_deactivate_another_users_project(auth_client, secondary_auth_client):
    """Deactivate another user's project returns 404"""
    with allure.step("Create project as second user"):
        project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        project_id = project['id']

    with allure.step("Attempt to deactivate as first user"):
        response = auth_client.patch(f'/api/projects/{project_id}/deactivate',
                                     handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404

    with allure.step("Verify project is still active for second user"):
        get_response = secondary_auth_client.get(f'/api/projects/{project_id}')
        assert get_response['active'] is True