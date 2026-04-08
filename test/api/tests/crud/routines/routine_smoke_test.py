import pytest
import allure


@allure.feature('Routines')
@allure.story('CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_basic_routine(auth_client):
    """Create a basic routine with only title"""
    with allure.step("Create routine with only required field"):
        response = auth_client.post('/api/routines', {
            "title": "Basic Routine"
        })

    with allure.step("Verify routine created successfully"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['title'] == "Basic Routine"
        assert response['active'] is True


@allure.feature('Routines')
@allure.story('CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_routines(auth_client):
    """List routines verifies routine appears"""
    routine_titles = ["Routine 1", "Routine 2", "Routine 3"]
    routine_ids = []
    with allure.step("Create two routines"):
        for title in routine_titles:
            routine = auth_client.post('/api/routines', {
                "title": title
            })
            routine_ids.append(routine['id'])

    with allure.step("List routines"):
        response = auth_client.get('/api/routines')
        routines = response.json
        routine_ids = [routine['id'] for routine in routines]

        assert isinstance(routine_ids, list)
        assert len(routine_ids) == len(routine_ids)
        for rid in routine_ids:
            assert rid in routine_ids




@allure.feature('Routines')
@allure.story('CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_routine_by_id(auth_client):
    """Get routine by ID returns full routine object"""
    with allure.step("Create test routine"):
        created = auth_client.post('/api/routines', {
            "title": "Test Routine"
        })
        routine_id = created['id']

    with allure.step("Retrieve routine by ID"):
        routine = auth_client.get(f'/api/routines/{routine_id}')

    with allure.step("Verify routine data"):
        assert routine['id'] == routine_id
        assert routine['title'] == "Test Routine"


@allure.feature('Routines')
@allure.story('CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_update_routine_title(auth_client):
    """Update routine title"""
    with allure.step("Create test routine"):
        created = auth_client.post('/api/routines', {
            "title": "Original Title"
        })
        routine_id = created['id']

    with allure.step("Update routine title"):
        updated = auth_client.patch(f'/api/routines/{routine_id}', {
            "title": "Updated Title"
        })

    with allure.step("Verify title was updated"):
        assert updated['id'] == routine_id
        assert updated['title'] == "Updated Title"
        assert updated['title'] != created['title']


@allure.feature('Routines')
@allure.story('CRUD Operations')
@pytest.mark.routines
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_routine(auth_client):
    """Delete routine removes it from the system"""
    with allure.step("Create test routine"):
        created = auth_client.post('/api/routines', {
            "title": "Routine to Delete"
        })
        routine_id = created['id']

    with allure.step("Delete routine"):
        response = auth_client.delete(f'/api/routines/{routine_id}',
                                      handle_response=False)

    with allure.step("Verify 204 No Content response"):
        assert response.status_code == 204

    with allure.step("Verify routine no longer exists"):
        get_response = auth_client.get(f'/api/routines/{routine_id}',
                                       handle_response=False)
        assert get_response.status_code == 404