import pytest
import allure
from test_utils.data_factories.entity_factory import create_task


@allure.feature('Principles')
@allure.story('Delete Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_principle_returns_204(auth_client):
    """Verify response is 204 No Content"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Principle to delete"
        })
        principle_id = created['id']

    with allure.step("Delete principle"):
        response = auth_client.delete(f'/api/principles/{principle_id}', handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204
        assert response.json is None  # 204 has no content


@allure.feature('Principles')
@allure.story('Delete Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_principle_actually_removes_it(auth_client):
    """Verify GET returns 404 afterward"""

    with allure.step("Create principle"):
        created = auth_client.post('/api/principles', data={
            "title": "Principle to delete"
        })
        principle_id = created['id']

    with allure.step("Verify principle exists"):
        get_response = auth_client.get(f'/api/principles/{principle_id}')
        assert get_response['id'] == principle_id

    with allure.step("Delete principle"):
        delete_response = auth_client.delete(f'/api/principles/{principle_id}', handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify principle no longer exists"):
        get_after_delete = auth_client.get(f'/api/principles/{principle_id}', handle_response=False)
        assert get_after_delete.status_code == 404


@allure.feature('Principles')
@allure.story('Delete Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_principle_with_attachments_cascade(auth_client):
    """Attach principle to task, delete principle, verify association removed"""

    with allure.step("Create principle"):
        principle = auth_client.post('/api/principles', data={
            "title": "Principle with attachments"
        })
        principle_id = principle['id']

    with allure.step("Create task"):
        task = create_task(auth_client, title="Task for principle attachment")
        task_id = task['id']

    with allure.step("Attach principle to task"):
        attach_response = auth_client.post('/api/principles/attach', data={
            "principle_id": principle_id,
            "target_type": "task",
            "target_id": task_id
        })
        assert attach_response['success'] is True

    with allure.step("Verify principle is attached to task"):
        task_check = auth_client.get(f'/api/tasks/{task_id}')
        task_principle_ids = [p['id'] for p in task_check.get('principles', [])]
        assert principle_id in task_principle_ids

    with allure.step("Delete principle"):
        delete_response = auth_client.delete(f'/api/principles/{principle_id}', handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify principle deleted"):
        get_principle = auth_client.get(f'/api/principles/{principle_id}', handle_response=False)
        assert get_principle.status_code == 404

    with allure.step("Verify association removed from task"):
        task_after = auth_client.get(f'/api/tasks/{task_id}')
        task_principle_ids_after = [p['id'] for p in task_after.get('principles', [])]
        assert principle_id not in task_principle_ids_after


@allure.feature('Principles')
@allure.story('Delete Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_principle(auth_client):
    """Verify 404 when deleting non-existent principle"""

    with allure.step("Attempt to delete non-existent principle"):
        response = auth_client.delete('/api/principles/999999', handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Principles')
@allure.story('Delete Principle')
@pytest.mark.principles
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_users_principle(auth_client, secondary_auth_client):
    """Verify 404 when deleting another user's principle"""

    with allure.step("Secondary user creates principle"):
        secondary_principle = secondary_auth_client.post('/api/principles', data={
            "title": "Secondary user principle"
        })
        secondary_principle_id = secondary_principle['id']

    with allure.step("Primary user attempts to delete secondary user's principle"):
        response = auth_client.delete(f'/api/principles/{secondary_principle_id}', handle_response=False)

    with allure.step("Verify 404 response (not authorized)"):
        assert response.status_code == 404

    with allure.step("Verify principle still exists for secondary user"):
        secondary_check = secondary_auth_client.get(f'/api/principles/{secondary_principle_id}')
        assert secondary_check['id'] == secondary_principle_id