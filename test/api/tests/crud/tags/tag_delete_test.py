import pytest
import allure
from utils.data_factories.entity_factory import create_task


@allure.feature('Tags')
@allure.story('Delete Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_tag_returns_204(auth_client):
    """Delete tag returns 204 No Content"""

    with allure.step("Create tag"):
        created = auth_client.post('/api/tags', data={"name": "test-tag"})
        tag_id = created['id']

    with allure.step("Delete tag"):
        response = auth_client.delete(f'/api/tags/{tag_id}', handle_response=False)

    with allure.step("Verify 204 response"):
        assert response.status_code == 204
        assert response.json is None


@allure.feature('Tags')
@allure.story('Delete Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_tag_actually_removes_it(auth_client):
    """Delete tag actually removes it from database"""

    with allure.step("Create tag"):
        created = auth_client.post('/api/tags', data={"name": "test-tag"})
        tag_id = created['id']

    with allure.step("Delete tag"):
        delete_response = auth_client.delete(f'/api/tags/{tag_id}', handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify tag no longer exists"):
        get_response = auth_client.get(f'/api/tags/{tag_id}', handle_response=False)
        assert get_response.status_code == 404


@allure.feature('Tags')
@allure.story('Delete Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_tag_with_attachments_cascade(auth_client):
    """Delete tag with attachments removes all associations (cascade)"""

    with allure.step("Create tag"):
        tag = auth_client.post('/api/tags', data={"name": "test-tag"})
        tag_id = tag['id']

    with allure.step("Create task and attach tag"):
        task = create_task(auth_client, title="Task with tag")
        task_id = task['id']

        attach_payload = {
            "tag_id": tag_id,
            "target_type": "task",
            "target_id": task_id
        }
        auth_client.post('/api/tags/attach', data=attach_payload)

    with allure.step("Verify tag is attached to task"):
        task_with_tag = auth_client.get(f'/api/tasks/{task_id}')
        assert 'tags' in task_with_tag
        tag_ids = [t['id'] for t in task_with_tag['tags']]
        assert tag_id in tag_ids

    with allure.step("Delete tag"):
        delete_response = auth_client.delete(f'/api/tags/{tag_id}', handle_response=False)
        assert delete_response.status_code == 204

    with allure.step("Verify tag removed from task"):
        task_after_delete = auth_client.get(f'/api/tasks/{task_id}')
        if 'tags' in task_after_delete and task_after_delete['tags']:
            remaining_tag_ids = [t['id'] for t in task_after_delete['tags']]
            assert tag_id not in remaining_tag_ids, \
                "Tag should be removed from task after deletion"
        else:
            # Tags array is empty or not present - association was removed
            assert True


@allure.feature('Tags')
@allure.story('Delete Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_nonexistent_tag(auth_client):
    """Delete nonexistent tag returns 404"""

    with allure.step("Attempt to delete non-existent tag"):
        response = auth_client.delete('/api/tags/999999', handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Tags')
@allure.story('Delete Tag')
@pytest.mark.tags
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_delete_another_users_tag(auth_client, secondary_auth_client):
    """Delete another user's tag returns 404"""

    with allure.step("Secondary user creates tag"):
        secondary_tag = secondary_auth_client.post('/api/tags', data={
            "name": "secondary-tag"
        })
        secondary_tag_id = secondary_tag['id']

    with allure.step("Primary user attempts to delete secondary user's tag"):
        response = auth_client.delete(f'/api/tags/{secondary_tag_id}', handle_response=False)

    with allure.step("Verify 404 error"):
        assert response.status_code == 404

    with allure.step("Verify secondary user's tag still exists"):
        verify_response = secondary_auth_client.get(f'/api/tags/{secondary_tag_id}')
        assert verify_response['id'] == secondary_tag_id