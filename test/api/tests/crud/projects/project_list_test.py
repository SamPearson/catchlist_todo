
import pytest
import allure


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_excludes_completed_by_default(auth_client):
    """List projects excludes completed projects by default"""
    with allure.step("Create active incomplete project"):
        incomplete = auth_client.post('/api/projects', {
            "title": "Incomplete project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        incomplete_id = incomplete['id']

    with allure.step("Create and complete an active project"):
        completed = auth_client.post('/api/projects', {
            "title": "Completed project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        completed_id = completed['id']
        auth_client.patch(f'/api/projects/{completed_id}/complete')

    with allure.step("List projects without include_completed parameter"):
        response = auth_client.get('/api/projects')

    with allure.step("Verify only incomplete project is returned"):
        project_ids = [p['id'] for p in response]
        assert incomplete_id in project_ids
        assert completed_id not in project_ids


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_with_include_completed_true(auth_client):
    """List projects with include_completed=true returns completed projects"""
    with allure.step("Create active incomplete project"):
        incomplete = auth_client.post('/api/projects', {
            "title": "Incomplete project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        incomplete_id = incomplete['id']

    with allure.step("Create and complete an active project"):
        completed = auth_client.post('/api/projects', {
            "title": "Completed project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        completed_id = completed['id']
        auth_client.patch(f'/api/projects/{completed_id}/complete')

    with allure.step("List projects with include_completed=true and include_inactive=true"):
        response = auth_client.get('/api/projects?include_completed=true&include_inactive=true')

    with allure.step("Verify both projects are returned"):
        project_ids = [p['id'] for p in response]
        assert incomplete_id in project_ids
        assert completed_id in project_ids


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_with_include_completed_false(auth_client):
    """List projects with include_completed=false explicitly excludes completed"""
    with allure.step("Create active incomplete project"):
        incomplete = auth_client.post('/api/projects', {
            "title": "Incomplete project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        incomplete_id = incomplete['id']

    with allure.step("Create and complete an active project"):
        completed = auth_client.post('/api/projects', {
            "title": "Completed project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        completed_id = completed['id']
        auth_client.patch(f'/api/projects/{completed_id}/complete')

    with allure.step("List projects with include_completed=false"):
        response = auth_client.get('/api/projects?include_completed=false')

    with allure.step("Verify only incomplete project is returned"):
        project_ids = [p['id'] for p in response]
        assert incomplete_id in project_ids
        assert completed_id not in project_ids


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_excludes_inactive_by_default(auth_client):
    """List projects excludes inactive projects by default"""
    with allure.step("Create active project"):
        active = auth_client.post('/api/projects', {
            "title": "Active project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        active_id = active['id']

    with allure.step("Create inactive project"):
        inactive = auth_client.post('/api/projects', {
            "title": "Inactive project"
        })
        inactive_id = inactive['id']

    with allure.step("List projects without include_inactive parameter"):
        response = auth_client.get('/api/projects')

    with allure.step("Verify only active project is returned"):
        project_ids = [p['id'] for p in response]
        assert active_id in project_ids
        assert inactive_id not in project_ids


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_with_include_inactive_true(auth_client):
    """List projects with include_inactive=true returns inactive projects"""
    with allure.step("Create active project"):
        active = auth_client.post('/api/projects', {
            "title": "Active project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        active_id = active['id']

    with allure.step("Create inactive project"):
        inactive = auth_client.post('/api/projects', {
            "title": "Inactive project"
        })
        inactive_id = inactive['id']

    with allure.step("List projects with include_inactive=true"):
        response = auth_client.get('/api/projects?include_inactive=true')

    with allure.step("Verify both projects are returned"):
        project_ids = [p['id'] for p in response]
        assert active_id in project_ids
        assert inactive_id in project_ids


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_with_include_inactive_false(auth_client):
    """List projects with include_inactive=false explicitly excludes inactive"""
    with allure.step("Create active project"):
        active = auth_client.post('/api/projects', {
            "title": "Active project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        active_id = active['id']

    with allure.step("Create inactive project"):
        inactive = auth_client.post('/api/projects', {
            "title": "Inactive project"
        })
        inactive_id = inactive['id']

    with allure.step("List projects with include_inactive=false"):
        response = auth_client.get('/api/projects?include_inactive=false')

    with allure.step("Verify only active project is returned"):
        project_ids = [p['id'] for p in response]
        assert active_id in project_ids
        assert inactive_id not in project_ids


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_with_both_filters_combined(auth_client):
    """List projects with both include_completed and include_inactive filters"""
    with allure.step("Create active incomplete project"):
        active_incomplete = auth_client.post('/api/projects', {
            "title": "Active incomplete",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        active_incomplete_id = active_incomplete['id']

    with allure.step("Create inactive incomplete project"):
        inactive_incomplete = auth_client.post('/api/projects', {
            "title": "Inactive incomplete"
        })
        inactive_incomplete_id = inactive_incomplete['id']

    with allure.step("Create inactive completed project"):
        inactive_completed = auth_client.post('/api/projects', {
            "title": "Inactive completed"
        })
        inactive_completed_id = inactive_completed['id']
        auth_client.patch(f'/api/projects/{inactive_completed_id}/complete')

    with allure.step("List with both filters true"):
        response = auth_client.get('/api/projects?include_completed=true&include_inactive=true')
        project_ids = [p['id'] for p in response]
        assert active_incomplete_id in project_ids
        assert inactive_incomplete_id in project_ids
        assert inactive_completed_id in project_ids

    with allure.step("List with default filters (both false)"):
        response = auth_client.get('/api/projects')
        project_ids = [p['id'] for p in response]
        assert active_incomplete_id in project_ids
        assert inactive_incomplete_id not in project_ids
        assert inactive_completed_id not in project_ids

    with allure.step("List with include_completed=true, include_inactive=false"):
        response = auth_client.get('/api/projects?include_completed=true&include_inactive=false')
        project_ids = [p['id'] for p in response]
        assert active_incomplete_id in project_ids
        assert inactive_incomplete_id not in project_ids
        assert inactive_completed_id not in project_ids

    with allure.step("List with include_completed=false, include_inactive=true"):
        response = auth_client.get('/api/projects?include_completed=false&include_inactive=true')
        project_ids = [p['id'] for p in response]
        assert active_incomplete_id in project_ids
        assert inactive_incomplete_id in project_ids
        assert inactive_completed_id not in project_ids


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_returns_empty_array(auth_client):
    """List projects returns empty array for user with no projects"""
    with allure.step("List projects for fresh user (no projects created yet)"):
        response = auth_client.get('/api/projects')
        projects = response.json

    with allure.step("Verify empty array returned"):
        assert isinstance(projects, list)
        assert len(projects) == 0


@allure.feature('Projects')
@allure.story('List Projects')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.list
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_list_projects_only_returns_users_own_projects(auth_client, secondary_auth_client):
    """List projects returns only the authenticated user's projects"""
    with allure.step("Create active project for first user"):
        user1_project = auth_client.post('/api/projects', {
            "title": "User 1 project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        user1_id = user1_project['id']

    with allure.step("Create active project for second user"):
        user2_project = secondary_auth_client.post('/api/projects', {
            "title": "User 2 project",
            "win_condition": "All tasks completed",
            "reason": "Important business goal",
            "next_step": "Start with phase 1",
            "active": True
        })
        user2_id = user2_project['id']

    with allure.step("List projects for first user"):
        user1_projects = auth_client.get('/api/projects')

    with allure.step("List projects for second user"):
        user2_projects = secondary_auth_client.get('/api/projects')

    with allure.step("Verify each user only sees their own projects"):
        user1_ids = [p['id'] for p in user1_projects]
        user2_ids = [p['id'] for p in user2_projects]

        assert user1_id in user1_ids
        assert user2_id not in user1_ids

        assert user2_id in user2_ids
        assert user1_id not in user2_ids