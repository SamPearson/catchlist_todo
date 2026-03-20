import pytest
import allure


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_project(auth_client):
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

        # Default values
        assert response['active'] is False
        assert isinstance(response['active'], bool)
        assert response['status'] == "open"
        assert isinstance(response['status'], str)
        assert response['completed'] is False
        assert isinstance(response['completed'], bool)

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
def test_list_projects(auth_client):
    """Retrieve all active projects for authenticated user"""
    with allure.step("Create multiple active test projects"):
        created_ids = []
        for i in range(3):
            project = auth_client.post('/api/projects', {
                "title": f"Test project {i+1}",
                "win_condition": "All tasks completed",
                "reason": "Important business goal",
                "next_step": "Start with phase 1",
                "active": True
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
            assert 'completed' in project
            assert 'active' in project
            assert 'status' in project
            assert 'created_at' in project
            assert 'updated_at' in project

    with allure.step("Verify created projects are in list"):
        retrieved_ids = [project['id'] for project in response]
        for created_id in created_ids:
            assert created_id in retrieved_ids


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_project(auth_client):
    """Retrieve a specific project by ID"""
    with allure.step("Create test project"):
        created = auth_client.post('/api/projects', {
            "title": "Project for retrieval",
            "description": "Test description"
        })
        project_id = created['id']

    with allure.step("Retrieve the project"):
        retrieved = auth_client.get(f'/api/projects/{project_id}')

    with allure.step("Verify retrieved project matches created project"):
        assert retrieved['id'] == project_id
        assert retrieved['title'] == created['title']
        assert retrieved['description'] == created['description']
        assert retrieved['completed'] == created['completed']
        assert retrieved['active'] == created['active']
        assert retrieved['status'] == created['status']
        assert retrieved['created_at'] == created['created_at']
        assert retrieved['updated_at'] == created['updated_at']


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_project(auth_client):
    """Update project title"""
    with allure.step("Create initial project"):
        created = auth_client.post('/api/projects', {
            "title": "Original title"
        })
        project_id = created['id']

    with allure.step("Update project"):
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
def test_delete_project(auth_client):
    """Delete project returns 204 No Content"""
    with allure.step("Create project to delete"):
        created = auth_client.post('/api/projects', {"title": "Delete me"})
        project_id = created['id']

    with allure.step("Delete project"):
        response = auth_client.delete(f'/api/projects/{project_id}',
                                      handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204

    with allure.step("Verify project is actually deleted"):
        get_response = auth_client.get(f'/api/projects/{project_id}',
                                       handle_response=False)
        assert get_response.status_code == 404


@allure.feature('Projects')
@allure.story('CRUD Operations')
@pytest.mark.projects
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_inactive_projects(auth_client):
    """Retrieve all inactive projects for authenticated user"""
    with allure.step("Create multiple inactive test projects"):
        created_ids = []
        for i in range(3):
            project = auth_client.post('/api/projects', {
                "title": f"Inactive test project {i+1}"
            })
            created_ids.append(project['id'])

    with allure.step("Retrieve all projects with include_inactive=true"):
        response = auth_client.get('/api/projects?include_inactive=true')

    with allure.step("Verify response structure"):
        assert isinstance(response, list)
        assert len(response) >= 3

        # Verify each project has required fields
        for project in response:
            assert project['id']
            assert project['title']
            assert 'completed' in project
            assert 'active' in project
            assert 'status' in project
            assert 'created_at' in project
            assert 'updated_at' in project

    with allure.step("Verify created inactive projects are in list"):
        retrieved_ids = [project['id'] for project in response]
        for created_id in created_ids:
            assert created_id in retrieved_ids