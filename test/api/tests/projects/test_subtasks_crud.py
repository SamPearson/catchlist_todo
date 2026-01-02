import pytest
import allure


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_subtask_with_required_fields(auth_client):
    """Create subtask with only required field (title)"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Prepare test data"):
        data = {"title": "Test subtask title"}

    with allure.step("Create new subtask"):
        response = auth_client.post(f'/api/projects/{project_id}/tasks', data)

    with allure.step("Verify response structure and values"):
        # Response contains ID and timestamps
        assert response['id']
        assert isinstance(response['id'], int)

        # Title matches input
        assert response['title'] == data['title']
        assert isinstance(response['title'], str)

        # Completion defaults to False
        assert response['completed'] is False
        assert isinstance(response['completed'], bool)

        # Timestamps present
        assert response['created_at']
        assert response['updated_at']
        assert isinstance(response['created_at'], str)
        assert isinstance(response['updated_at'], str)

        # Optional fields present but null
        assert response['description'] is None
        assert response['completed_at'] is None

        # Verify belongs to correct project
        assert response['project_id'] == project_id


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_subtask_with_description(auth_client):
    """Create subtask with title and description"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Prepare test data"):
        data = {
            "title": "Subtask with description",
            "description": "This is a detailed description of the subtask"
        }

    with allure.step("Create new subtask"):
        response = auth_client.post(f'/api/projects/{project_id}/tasks', data)

    with allure.step("Verify description is stored"):
        assert response['description'] == data['description']
        assert isinstance(response['description'], str)
        assert response['project_id'] == project_id


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_subtask_with_completed_status(auth_client):
    """Create subtask with completed status"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Prepare test data"):
        data = {
            "title": "Completed subtask",
            "completed": True
        }

    with allure.step("Create new subtask"):
        response = auth_client.post(f'/api/projects/{project_id}/tasks', data)

    with allure.step("Verify completed status"):
        assert response['completed'] is True
        assert response['project_id'] == project_id


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_multiple_subtasks_in_project(auth_client):
    """Create multiple subtasks in same project"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create first subtask"):
        subtask1 = auth_client.post(f'/api/projects/{project_id}/tasks',
                                    {"title": "Subtask 1"})
        subtask1_id = subtask1['id']

    with allure.step("Create second subtask"):
        subtask2 = auth_client.post(f'/api/projects/{project_id}/tasks',
                                    {"title": "Subtask 2"})
        subtask2_id = subtask2['id']

    with allure.step("Verify subtasks are independent"):
        assert subtask1_id != subtask2_id
        assert subtask1['title'] != subtask2['title']
        assert subtask1['project_id'] == project_id
        assert subtask2['project_id'] == project_id
        # Timestamps should be close but not identical
        assert subtask1['created_at'] <= subtask2['created_at']


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_create_subtasks_in_different_projects(auth_client):
    """Create subtasks with same title in different projects"""
    with allure.step("Create first project"):
        project1 = auth_client.post('/api/projects', {"title": "Project 1"})
        project1_id = project1['id']

    with allure.step("Create second project"):
        project2 = auth_client.post('/api/projects', {"title": "Project 2"})
        project2_id = project2['id']

    with allure.step("Create subtask in first project"):
        subtask1 = auth_client.post(f'/api/projects/{project1_id}/tasks',
                                    {"title": "Same title"})

    with allure.step("Create subtask in second project"):
        subtask2 = auth_client.post(f'/api/projects/{project2_id}/tasks',
                                    {"title": "Same title"})

    with allure.step("Verify subtasks are in correct projects"):
        assert subtask1['id'] != subtask2['id']
        assert subtask1['project_id'] == project1_id
        assert subtask2['project_id'] == project2_id


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_subtasks_in_project(auth_client):
    """Retrieve all subtasks for a project"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create multiple test subtasks"):
        created_ids = []
        for i in range(3):
            subtask = auth_client.post(f'/api/projects/{project_id}/tasks', {
                "title": f"Test subtask {i+1}"
            })
            created_ids.append(subtask['id'])

    with allure.step("Retrieve all subtasks in project"):
        response = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify response structure"):
        assert isinstance(response, list)
        assert len(response) >= 3

        # Verify each subtask has required fields
        for subtask in response:
            assert subtask['id']
            assert subtask['title']
            assert 'completed' in subtask
            assert 'created_at' in subtask
            assert 'updated_at' in subtask
            assert subtask['project_id'] == project_id

    with allure.step("Verify created subtasks are in list"):
        retrieved_ids = [s['id'] for s in response]
        for created_id in created_ids:
            assert created_id in retrieved_ids


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_subtasks_empty_list_for_new_project(auth_client):
    """Retrieve subtasks from project with none returns empty list"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Empty project"})
        project_id = project['id']

    with allure.step("Retrieve subtasks from empty project"):
        response = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify empty list"):
        assert isinstance(response, list)
        assert len(response) == 0


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_subtasks_exclude_completed_by_default(auth_client):
    """Get subtasks filters out completed by default"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create active subtask"):
        active = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Active subtask"
        })
        active_id = active['id']

    with allure.step("Create and complete a subtask"):
        completed = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Completed subtask"
        })
        completed_id = completed['id']
        auth_client.put(f'/api/projects/{project_id}/tasks/{completed_id}', {
            "completed": True
        })

    with allure.step("Retrieve subtasks without filter"):
        response = auth_client.get(f'/api/projects/{project_id}/tasks')

    with allure.step("Verify completed subtask is excluded"):
        retrieved_ids = [s['id'] for s in response]
        assert active_id in retrieved_ids
        assert completed_id not in retrieved_ids


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_get_subtasks_include_completed_with_parameter(auth_client):
    """Get subtasks with include_completed=true returns completed subtasks"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create and complete a subtask"):
        completed = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Completed subtask"
        })
        completed_id = completed['id']
        auth_client.put(f'/api/projects/{project_id}/tasks/{completed_id}', {
            "completed": True
        })

    with allure.step("Retrieve subtasks with include_completed=true"):
        response = auth_client.get(
            f'/api/projects/{project_id}/tasks?include_completed=true'
        )

    with allure.step("Verify completed subtask is included"):
        retrieved_ids = [s['id'] for s in response]
        assert completed_id in retrieved_ids


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_subtask_title(auth_client):
    """Update subtask title"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create initial subtask"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Original title"
        })
        subtask_id = created['id']

    with allure.step("Update subtask title"):
        updated = auth_client.put(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            {"title": "Updated title"}
        )

    with allure.step("Verify update"):
        assert updated['id'] == subtask_id
        assert updated['title'] == "Updated title"
        assert updated['project_id'] == project_id
        assert updated['created_at'] == created['created_at']
        assert updated['updated_at'] >= created['updated_at']


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_subtask_description(auth_client):
    """Update subtask description"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask with description"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Test subtask",
            "description": "Original description"
        })
        subtask_id = created['id']

    with allure.step("Update description"):
        updated = auth_client.put(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            {"description": "New description"}
        )

    with allure.step("Verify description updated"):
        assert updated['description'] == "New description"
        assert updated['title'] == created['title']  # Title unchanged
        assert updated['project_id'] == project_id


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_subtask_completion_status(auth_client):
    """Update subtask completion status"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create incomplete subtask"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Test subtask",
            "completed": False
        })
        subtask_id = created['id']

    with allure.step("Mark subtask as complete"):
        updated = auth_client.put(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            {"completed": True}
        )

    with allure.step("Verify completion status changed"):
        assert updated['completed'] is True
        assert updated['title'] == created['title']  # Title unchanged
        assert updated['project_id'] == project_id


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_subtask_sets_completed_at(auth_client):
    """Update subtask to completed sets completed_at timestamp"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create incomplete subtask"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Test subtask"
        })
        subtask_id = created['id']
        assert created['completed_at'] is None

    with allure.step("Mark subtask as complete"):
        updated = auth_client.put(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            {"completed": True}
        )

    with allure.step("Verify completed_at is set"):
        assert updated['completed_at'] is not None
        assert isinstance(updated['completed_at'], str)


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_multiple_subtask_fields(auth_client):
    """Update multiple subtask fields at once"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create initial subtask"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks', {
            "title": "Original",
            "description": "Original description",
            "completed": False
        })
        subtask_id = created['id']

    with allure.step("Update multiple fields"):
        updated = auth_client.put(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            {
                "title": "New title",
                "description": "New description",
                "completed": True
            }
        )

    with allure.step("Verify all updates applied"):
        assert updated['title'] == "New title"
        assert updated['description'] == "New description"
        assert updated['completed'] is True
        assert updated['project_id'] == project_id


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_update_preserves_timestamps(auth_client):
    """Verify created_at doesn't change on update"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks',
                                   {"title": "Test"})
        original_created_at = created['created_at']
        subtask_id = created['id']

    with allure.step("Update subtask"):
        updated = auth_client.put(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            {"title": "Updated"}
        )

    with allure.step("Verify timestamps"):
        assert updated['created_at'] == original_created_at
        assert updated['updated_at'] >= original_created_at


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_subtask_returns_204(auth_client):
    """Delete subtask returns 204 No Content"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask to delete"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks',
                                   {"title": "Delete me"})
        subtask_id = created['id']

    with allure.step("Delete subtask"):
        response = auth_client.delete(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            handle_response=False
        )

    with allure.step("Verify 204 response"):
        assert response.status_code == 204


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_subtask_removes_from_list(auth_client):
    """Verify deleted subtask no longer appears in list"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create subtask"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks',
                                   {"title": "To delete"})
        subtask_id = created['id']

    with allure.step("Verify subtask in list"):
        subtasks_before = auth_client.get(f'/api/projects/{project_id}/tasks')
        subtask_ids_before = [s['id'] for s in subtasks_before]
        assert subtask_id in subtask_ids_before

    with allure.step("Delete subtask"):
        auth_client.delete(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            handle_response=False
        )

    with allure.step("Verify subtask removed from list"):
        subtasks_after = auth_client.get(f'/api/projects/{project_id}/tasks')
        subtask_ids_after = [s['id'] for s in subtasks_after]
        assert subtask_id not in subtask_ids_after


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_subtask_cannot_be_retrieved(auth_client):
    """Verify deleted subtask returns 404 on GET"""
    with allure.step("Create test project"):
        project = auth_client.post('/api/projects', {"title": "Test project"})
        project_id = project['id']

    with allure.step("Create and delete subtask"):
        created = auth_client.post(f'/api/projects/{project_id}/tasks',
                                   {"title": "Delete me"})
        subtask_id = created['id']
        auth_client.delete(
            f'/api/projects/{project_id}/tasks/{subtask_id}',
            handle_response=False
        )

    with allure.step("Attempt to retrieve deleted subtask via project list"):
        subtasks = auth_client.get(
            f'/api/projects/{project_id}/tasks?include_completed=true'
        )
        subtask_ids = [s['id'] for s in subtasks]

    with allure.step("Verify subtask is gone"):
        assert subtask_id not in subtask_ids


@allure.feature('Projects')
@allure.story('Subtask CRUD Operations')
@pytest.mark.projects
@pytest.mark.subtasks
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_subtask_belongs_to_correct_project(auth_client):
    """Verify subtask is correctly associated with its project"""
    with allure.step("Create first project"):
        project1 = auth_client.post('/api/projects', {"title": "Project 1"})
        project1_id = project1['id']

    with allure.step("Create second project"):
        project2 = auth_client.post('/api/projects', {"title": "Project 2"})
        project2_id = project2['id']

    with allure.step("Create subtask in first project"):
        subtask1 = auth_client.post(f'/api/projects/{project1_id}/tasks',
                                    {"title": "Subtask 1"})
        subtask1_id = subtask1['id']

    with allure.step("Create subtask in second project"):
        subtask2 = auth_client.post(f'/api/projects/{project2_id}/tasks',
                                    {"title": "Subtask 2"})
        subtask2_id = subtask2['id']

    with allure.step("Verify subtasks in correct projects"):
        # Get all subtasks from project 1
        project1_subtasks = auth_client.get(
            f'/api/projects/{project1_id}/tasks?include_completed=true'
        )
        project1_ids = [s['id'] for s in project1_subtasks]

        # Get all subtasks from project 2
        project2_subtasks = auth_client.get(
            f'/api/projects/{project2_id}/tasks?include_completed=true'
        )
        project2_ids = [s['id'] for s in project2_subtasks]

        # Verify separation
        assert subtask1_id in project1_ids
        assert subtask1_id not in project2_ids
        assert subtask2_id in project2_ids
        assert subtask2_id not in project1_ids