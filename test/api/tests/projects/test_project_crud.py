import pytest
import allure


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_project_with_required_fields(auth_client):
    """Create project with only required field (title)"""
    with allure.step("Prepare test data"):
        data = {"title": "Test project title"}

    with allure.step("Create new project"):
        response = auth_client.post('/api/projects', data)

    with allure.step("Verify response structure and values"):
        # Response contains ID and timestamps
        assert response['id']
        assert isinstance(response['id'], int)

        # Title matches input
        assert response['title'] == data['title']
        assert isinstance(response['title'], str)

        # Active defaults to True
        assert response['active'] is True
        assert isinstance(response['active'], bool)

        # Timestamps present
        assert response['created_at']
        assert response['updated_at']
        assert isinstance(response['created_at'], str)
        assert isinstance(response['updated_at'], str)

        # Optional fields present but null
        assert response['description'] is None
        assert response['win_condition'] is None
        assert response['reason'] is None
        assert response['next_step'] is None
        assert response['completed_at'] is None

        # Array fields present and empty
        assert response['tags'] == []
        assert response['principles'] == []
        assert isinstance(response['tags'], list)
        assert isinstance(response['principles'], list)


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_project_with_description(auth_client):
    """Create project with title and description"""
    with allure.step("Prepare test data"):
        data = {
            "title": "Project with description",
            "description": "This is a detailed description of the project"
        }

    with allure.step("Create new project"):
        response = auth_client.post('/api/projects', data)

    with allure.step("Verify description is stored"):
        assert response['description'] == data['description']
        assert isinstance(response['description'], str)


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_project_with_all_fields(auth_client):
    """Create project with all optional fields"""
    with allure.step("Prepare test data"):
        data = {
            "title": "Fully detailed project",
            "description": "Complete project description",
            "win_condition": "Project succeeds when all milestones are met",
            "reason": "This project will improve team efficiency",
            "next_step": "Set up project infrastructure"
        }

    with allure.step("Create new project"):
        response = auth_client.post('/api/projects', data)

    with allure.step("Verify all fields are stored"):
        assert response['title'] == data['title']
        assert response['description'] == data['description']
        assert response['win_condition'] == data['win_condition']
        assert response['reason'] == data['reason']
        assert response['next_step'] == data['next_step']
        assert response['active'] is True


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_multiple_projects(auth_client):
    """Create multiple projects to verify independence"""
    with allure.step("Create first project"):
        project1 = auth_client.post('/api/projects', {"title": "Project 1"})
        project1_id = project1['id']

    with allure.step("Create second project"):
        project2 = auth_client.post('/api/projects', {"title": "Project 2"})
        project2_id = project2['id']

    with allure.step("Verify projects are independent"):
        assert project1_id != project2_id
        assert project1['title'] != project2['title']
        # Timestamps should be close but not identical
        assert project1['created_at'] <= project2['created_at']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_project_by_id(auth_client):
    """Retrieve a specific project by ID"""
    with allure.step("Create test project"):
        created = auth_client.post('/api/projects', {
            "title": "Project for retrieval",
            "description": "Test description",
            "win_condition": "Test win condition"
        })
        project_id = created['id']

    with allure.step("Retrieve the project"):
        retrieved = auth_client.get(f'/api/projects/{project_id}')

    with allure.step("Verify retrieved project matches created project"):
        assert retrieved['id'] == project_id
        assert retrieved['title'] == created['title']
        assert retrieved['description'] == created['description']
        assert retrieved['win_condition'] == created['win_condition']
        assert retrieved['active'] == created['active']
        assert retrieved['created_at'] == created['created_at']
        assert retrieved['updated_at'] == created['updated_at']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_projects_returns_list(auth_client):
    """Retrieve all projects for authenticated user"""
    with allure.step("Create multiple test projects"):
        created_ids = []
        for i in range(3):
            project = auth_client.post('/api/projects', {
                "title": f"Test project {i+1}"
            })
            created_ids.append(project['id'])

    with allure.step("Retrieve all projects"):
        response = auth_client.get('/api/projects')

    with allure.step("Verify response structure"):
        assert isinstance(response, list)
        assert len(response) >= 3

        # Verify each project has required fields
        for project in response:
            assert project['id']
            assert project['title']
            assert 'active' in project
            assert 'created_at' in project
            assert 'updated_at' in project
            assert 'tags' in project
            assert 'principles' in project

    with allure.step("Verify created projects are in list"):
        retrieved_ids = [p['id'] for p in response]
        for created_id in created_ids:
            assert created_id in retrieved_ids


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_projects_exclude_inactive_by_default(auth_client):
    """List projects filters out inactive projects by default"""
    with allure.step("Create active project"):
        active_project = auth_client.post('/api/projects', {
            "title": "Active project"
        })
        active_id = active_project['id']

    with allure.step("Create and deactivate a project"):
        inactive_project = auth_client.post('/api/projects', {
            "title": "Inactive project"
        })
        inactive_id = inactive_project['id']
        auth_client.put(f'/api/projects/{inactive_id}', {
            "active": False
        })

    with allure.step("Retrieve all projects without filter"):
        response = auth_client.get('/api/projects')

    with allure.step("Verify inactive project is excluded"):
        retrieved_ids = [p['id'] for p in response]
        assert active_id in retrieved_ids
        assert inactive_id not in retrieved_ids


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_projects_include_inactive_with_parameter(auth_client):
    """List projects with include_completed=true returns inactive projects"""
    with allure.step("Create and deactivate a project"):
        inactive_project = auth_client.post('/api/projects', {
            "title": "Inactive project"
        })
        inactive_id = inactive_project['id']
        auth_client.put(f'/api/projects/{inactive_id}', {
            "active": False
        })

    with allure.step("Retrieve all projects with include_completed=true"):
        response = auth_client.get('/api/projects?include_completed=true')

    with allure.step("Verify inactive project is included"):
        retrieved_ids = [p['id'] for p in response]
        assert inactive_id in retrieved_ids


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
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

    with allure.step("Verify update"):
        assert updated['id'] == project_id
        assert updated['title'] == "Updated title"
        assert updated['created_at'] == created['created_at']
        assert updated['updated_at'] >= created['updated_at']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_project_description(auth_client):
    """Update project description"""
    with allure.step("Create project with description"):
        created = auth_client.post('/api/projects', {
            "title": "Test project",
            "description": "Original description"
        })
        project_id = created['id']

    with allure.step("Update description"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "description": "New description"
        })

    with allure.step("Verify description updated"):
        assert updated['description'] == "New description"
        assert updated['title'] == created['title']  # Title unchanged


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_project_win_condition(auth_client):
    """Update project win condition"""
    with allure.step("Create project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project",
            "win_condition": "Original win condition"
        })
        project_id = created['id']

    with allure.step("Update win condition"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "win_condition": "New win condition"
        })

    with allure.step("Verify win condition updated"):
        assert updated['win_condition'] == "New win condition"
        assert updated['title'] == created['title']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_project_reason(auth_client):
    """Update project reason"""
    with allure.step("Create project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project",
            "reason": "Original reason"
        })
        project_id = created['id']

    with allure.step("Update reason"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "reason": "New reason"
        })

    with allure.step("Verify reason updated"):
        assert updated['reason'] == "New reason"
        assert updated['title'] == created['title']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_project_next_step(auth_client):
    """Update project next step"""
    with allure.step("Create project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project",
            "next_step": "Original next step"
        })
        project_id = created['id']

    with allure.step("Update next step"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "next_step": "New next step"
        })

    with allure.step("Verify next step updated"):
        assert updated['next_step'] == "New next step"
        assert updated['title'] == created['title']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_project_active_status(auth_client):
    """Update project active status"""
    with allure.step("Create active project"):
        created = auth_client.post('/api/projects', {
            "title": "Test project"
        })
        project_id = created['id']
        assert created['active'] is True

    with allure.step("Mark project as inactive"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "active": False
        })

    with allure.step("Verify active status changed"):
        assert updated['active'] is False
        assert updated['title'] == created['title']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_multiple_project_fields(auth_client):
    """Update multiple project fields at once"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Original",
            "description": "Original description",
            "win_condition": "Original condition",
            "reason": "Original reason",
            "next_step": "Original step",
            "active": True
        })
        project_id = created['id']

    with allure.step("Update multiple fields"):
        updated = auth_client.put(f'/api/projects/{project_id}', {
            "title": "New title",
            "description": "New description",
            "win_condition": "New condition",
            "reason": "New reason",
            "next_step": "New step",
            "active": False
        })

    with allure.step("Verify all updates applied"):
        assert updated['title'] == "New title"
        assert updated['description'] == "New description"
        assert updated['win_condition'] == "New condition"
        assert updated['reason'] == "New reason"
        assert updated['next_step'] == "New step"
        assert updated['active'] is False


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_preserves_timestamps(auth_client):
    """Verify created_at doesn't change on update"""
    with allure.step("Create project"):
        created = auth_client.post('/api/projects', {"title": "Test"})
        original_created_at = created['created_at']

    with allure.step("Update project"):
        updated = auth_client.put(f'/api/projects/{created["id"]}', {
            "title": "Updated"
        })

    with allure.step("Verify timestamps"):
        assert updated['created_at'] == original_created_at
        assert updated['updated_at'] >= original_created_at


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_project_returns_204(auth_client):
    """Delete project returns 204 No Content"""
    with allure.step("Create project to delete"):
        created = auth_client.post('/api/projects', {"title": "Delete me"})
        project_id = created['id']

    with allure.step("Delete project"):
        response = auth_client.delete(f'/api/projects/{project_id}',
                                      handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_project_removes_from_list(auth_client):
    """Verify deleted project no longer appears in list"""
    with allure.step("Create project"):
        created = auth_client.post('/api/projects', {"title": "To delete"})
        project_id = created['id']

    with allure.step("Verify project in list"):
        projects_before = auth_client.get('/api/projects')
        project_ids_before = [p['id'] for p in projects_before]
        assert project_id in project_ids_before

    with allure.step("Delete project"):
        auth_client.delete(f'/api/projects/{project_id}', handle_response=False)

    with allure.step("Verify project removed from list"):
        projects_after = auth_client.get('/api/projects')
        project_ids_after = [p['id'] for p in projects_after]
        assert project_id not in project_ids_after


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_project_cannot_be_retrieved(auth_client):
    """Verify deleted project returns 404 on GET"""
    with allure.step("Create and delete project"):
        created = auth_client.post('/api/projects', {"title": "Delete me"})
        project_id = created['id']
        auth_client.delete(f'/api/projects/{project_id}', handle_response=False)

    with allure.step("Attempt to retrieve deleted project"):
        response = auth_client.get(f'/api/projects/{project_id}',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404