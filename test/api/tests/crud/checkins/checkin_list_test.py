import pytest
import allure
from datetime import datetime, timedelta, timezone
from utils.data_factories.entity_factory import create_task, create_project, create_checkin


# Tests for GET /api/checkins/target (target-specific listing)

@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_returns_empty_array(auth_client):
    """List checkins for target with no checkins returns empty array"""

    with allure.step("Create target task without checkins"):
        task = create_task(auth_client, title="Task with no checkins")
        task_id = task['id']

    with allure.step("List checkins for task"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}'
        )
        checkins = response.json

    with allure.step("Verify empty array returned"):
        assert isinstance(checkins, list)
        assert len(checkins) == 0


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_only_returns_users_own_checkins(auth_client, secondary_auth_client):
    """List checkins only returns user's own checkins"""

    with allure.step("Primary user creates task and checkin"):
        primary_task = create_task(auth_client, title="Primary user task")
        primary_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=primary_task['id'],
            note="Primary user checkin"
        )

    with allure.step("Secondary user creates task and checkin"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_checkin = create_checkin(
            secondary_auth_client,
            target_type="task",
            target_id=secondary_task['id'],
            note="Secondary user checkin"
        )

    with allure.step("Primary user lists their checkins"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={primary_task["id"]}'
        )
        primary_checkins = response.json

    with allure.step("Verify primary user only sees their own checkin"):
        primary_ids = [c['id'] for c in primary_checkins]
        assert primary_checkin['id'] in primary_ids
        assert secondary_checkin['id'] not in primary_ids


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_ordered_by_occurred_at_desc(auth_client):
    """List checkins ordered by occurred_at descending (most recent first)"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for ordering test")
        task_id = task['id']

    with allure.step("Create checkins with different occurred_at times"):
        # Create checkins with explicit occurred_at times
        now = datetime.now(timezone.utc)

        checkin1 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Oldest checkin",
            occurred_at=(now - timedelta(hours=3)).isoformat()
        )

        checkin2 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Middle checkin",
            occurred_at=(now - timedelta(hours=2)).isoformat()
        )

        checkin3 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Most recent checkin",
            occurred_at=(now - timedelta(hours=1)).isoformat()
        )

    with allure.step("List checkins"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}'
        )
        checkins = response.json

    with allure.step("Verify ordering by occurred_at descending"):
        assert len(checkins) == 3
        assert checkins[0]['id'] == checkin3['id']  # Most recent first
        assert checkins[1]['id'] == checkin2['id']  # Middle
        assert checkins[2]['id'] == checkin1['id']  # Oldest last


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_ordered_by_created_at_desc_when_occurred_at_equal(auth_client):
    """List checkins ordered by created_at DESC when occurred_at is equal"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for secondary ordering test")
        task_id = task['id']

    with allure.step("Create checkins with same occurred_at"):
        # Use the same occurred_at for all checkins
        same_time = datetime.now(timezone.utc).isoformat()

        checkin1 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="First created",
            occurred_at=same_time
        )

        checkin2 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Second created",
            occurred_at=same_time
        )

        checkin3 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Third created",
            occurred_at=same_time
        )

    with allure.step("List checkins"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}'
        )
        checkins = response.json

    with allure.step("Verify secondary ordering by created_at descending"):
        assert len(checkins) == 3
        # Most recently created should be first
        assert checkins[0]['id'] == checkin3['id']
        assert checkins[1]['id'] == checkin2['id']
        assert checkins[2]['id'] == checkin1['id']


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_with_limit_parameter(auth_client):
    """List checkins with limit parameter returns correct number"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for limit test")
        task_id = task['id']

    with allure.step("Create 10 checkins"):
        for i in range(10):
            create_checkin(
                auth_client,
                target_type="task",
                target_id=task_id,
                note=f"Checkin {i + 1}"
            )

    with allure.step("List checkins with limit=5"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&limit=5'
        )
        checkins = response.json

    with allure.step("Verify only 5 checkins returned"):
        assert len(checkins) == 5


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_with_offset_parameter(auth_client):
    """List checkins with offset parameter skips correct number"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for offset test")
        task_id = task['id']

    with allure.step("Create 10 checkins"):
        checkin_ids = []
        for i in range(10):
            checkin = create_checkin(
                auth_client,
                target_type="task",
                target_id=task_id,
                note=f"Checkin {i + 1}"
            )
            checkin_ids.append(checkin['id'])

    with allure.step("List all checkins"):
        all_response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}'
        )
        all_checkins = all_response.json

    with allure.step("List checkins with offset=5"):
        offset_response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&offset=5'
        )
        offset_checkins = offset_response.json

    with allure.step("Verify first 5 checkins were skipped"):
        assert len(offset_checkins) == 5
        # The offset checkins should match the last 5 from all_checkins
        assert offset_checkins[0]['id'] == all_checkins[5]['id']


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_with_limit_and_offset_together(auth_client):
    """List checkins with both limit and offset works correctly"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for pagination test")
        task_id = task['id']

    with allure.step("Create 20 checkins"):
        for i in range(20):
            create_checkin(
                auth_client,
                target_type="task",
                target_id=task_id,
                note=f"Checkin {i + 1}"
            )

    with allure.step("List all checkins"):
        all_response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}'
        )
        all_checkins = all_response.json

    with allure.step("List checkins with offset=5 and limit=10"):
        paginated_response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&offset=5&limit=10'
        )
        paginated_checkins = paginated_response.json

    with allure.step("Verify pagination works correctly"):
        assert len(paginated_checkins) == 10
        # Should match checkins 6-15 from the full list
        assert paginated_checkins[0]['id'] == all_checkins[5]['id']
        assert paginated_checkins[9]['id'] == all_checkins[14]['id']


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_verifies_default_limit(auth_client):
    """List checkins returns only 50 by default when more exist"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for default limit test")
        task_id = task['id']

    with allure.step("Create 60 checkins"):
        for i in range(60):
            create_checkin(
                auth_client,
                target_type="task",
                target_id=task_id,
                note=f"Checkin {i + 1}"
            )

    with allure.step("List checkins without limit parameter"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}'
        )
        checkins = response.json

    with allure.step("Verify only 50 checkins returned by default"):
        assert len(checkins) == 50


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_without_target_type(auth_client):
    """List checkins without target_type returns 400"""

    with allure.step("Attempt to list checkins without target_type"):
        response = auth_client.get(
            '/api/checkins/target?target_id=123',
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_without_target_id(auth_client):
    """List checkins without target_id returns 400"""

    with allure.step("Attempt to list checkins without target_id"):
        response = auth_client.get(
            '/api/checkins/target?target_type=task',
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_with_invalid_target_id(auth_client):
    """List checkins with invalid target_id (not integer) returns 400"""

    with allure.step("Attempt to list checkins with non-integer target_id"):
        response = auth_client.get(
            '/api/checkins/target?target_type=task&target_id=invalid',
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_with_invalid_limit(auth_client):
    """List checkins with invalid limit (not integer) returns 400"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for invalid limit test")
        task_id = task['id']

    with allure.step("Attempt to list checkins with non-integer limit"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&limit=invalid',
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_with_invalid_offset(auth_client):
    """List checkins with invalid offset (not integer) returns 400"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for invalid offset test")
        task_id = task['id']

    with allure.step("Attempt to list checkins with non-integer offset"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&offset=invalid',
            handle_response=False
        )

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_for_nonexistent_target(auth_client):
    """List checkins for nonexistent target returns 404"""

    with allure.step("Attempt to list checkins for nonexistent task"):
        response = auth_client.get(
            '/api/checkins/target?target_type=task&target_id=999999',
            handle_response=False
        )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_for_another_users_target(auth_client, secondary_auth_client):
    """List checkins for another user's target returns 404"""

    with allure.step("Secondary user creates task"):
        secondary_task = create_task(secondary_auth_client, title="Secondary user task")
        secondary_task_id = secondary_task['id']

    with allure.step("Primary user attempts to list checkins for secondary user's task"):
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={secondary_task_id}',
            handle_response=False
        )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_target_with_start_date(auth_client):
    """List checkins for target with start_date filter"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for start_date test")
        task_id = task['id']

    with allure.step("Create checkins with different dates"):
        now = datetime.now(timezone.utc)

        # Old checkin (should be filtered out)
        old_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Old checkin",
            occurred_at=(now - timedelta(days=10)).isoformat()
        )

        # Recent checkin (should be included)
        recent_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Recent checkin",
            occurred_at=(now - timedelta(days=2)).isoformat()
        )

    with allure.step("List checkins with start_date=5 days ago"):
        start_date = (now - timedelta(days=5)).strftime('%Y-%m-%d')
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&start_date={start_date}'
        )
        checkins = response.json

    with allure.step("Verify only recent checkin returned"):
        checkin_ids = [c['id'] for c in checkins]
        assert recent_checkin['id'] in checkin_ids
        assert old_checkin['id'] not in checkin_ids


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_target_with_end_date(auth_client):
    """List checkins for target with end_date filter"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for end_date test")
        task_id = task['id']

    with allure.step("Create checkins with different dates"):
        now = datetime.now(timezone.utc)

        # Old checkin (should be included)
        old_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Old checkin",
            occurred_at=(now - timedelta(days=10)).isoformat()
        )

        # Recent checkin (should be filtered out)
        recent_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Recent checkin",
            occurred_at=(now - timedelta(days=2)).isoformat()
        )

    with allure.step("List checkins with end_date=5 days ago"):
        end_date = (now - timedelta(days=5)).strftime('%Y-%m-%d')
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&end_date={end_date}'
        )
        checkins = response.json

    with allure.step("Verify only old checkin returned"):
        checkin_ids = [c['id'] for c in checkins]
        assert old_checkin['id'] in checkin_ids
        assert recent_checkin['id'] not in checkin_ids


@allure.feature('Checkins')
@allure.story('List Checkins for Target')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_checkins_target_with_date_range(auth_client):
    """List checkins for target with both start_date and end_date"""

    with allure.step("Create target task"):
        task = create_task(auth_client, title="Task for date range test")
        task_id = task['id']

    with allure.step("Create checkins across different dates"):
        now = datetime.now(timezone.utc)

        # Too old (before range)
        too_old = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Too old",
            occurred_at=(now - timedelta(days=15)).isoformat()
        )

        # In range
        in_range = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="In range",
            occurred_at=(now - timedelta(days=7)).isoformat()
        )

        # Too recent (after range)
        too_recent = create_checkin(
            auth_client,
            target_type="task",
            target_id=task_id,
            note="Too recent",
            occurred_at=(now - timedelta(days=2)).isoformat()
        )

    with allure.step("List checkins with date range"):
        start_date = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = (now - timedelta(days=5)).strftime('%Y-%m-%d')
        response = auth_client.get(
            f'/api/checkins/target?target_type=task&target_id={task_id}&start_date={start_date}&end_date={end_date}'
        )
        checkins = response.json

    with allure.step("Verify only in-range checkin returned"):
        checkin_ids = [c['id'] for c in checkins]
        assert in_range['id'] in checkin_ids
        assert too_old['id'] not in checkin_ids
        assert too_recent['id'] not in checkin_ids


@allure.feature('Checkins')
@allure.story('List All Checkins')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_all_checkins_for_user(auth_client):
    """List all checkins for user across multiple targets"""

    with allure.step("Create multiple targets with checkins"):
        task1 = create_task(auth_client, title="Task 1")
        task2 = create_task(auth_client, title="Task 2")
        project = create_project(auth_client, title="Project 1")

        checkin1 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task1['id'],
            note="Task 1 checkin"
        )

        checkin2 = create_checkin(
            auth_client,
            target_type="task",
            target_id=task2['id'],
            note="Task 2 checkin"
        )

        checkin3 = create_checkin(
            auth_client,
            target_type="project",
            target_id=project['id'],
            note="Project checkin"
        )

    with allure.step("List all checkins"):
        response = auth_client.get('/api/checkins')
        all_checkins = response.json

    with allure.step("Verify all checkins returned"):
        checkin_ids = [c['id'] for c in all_checkins]
        assert checkin1['id'] in checkin_ids
        assert checkin2['id'] in checkin_ids
        assert checkin3['id'] in checkin_ids
        assert len(all_checkins) >= 3


@allure.feature('Checkins')
@allure.story('List All Checkins')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_all_checkins_only_returns_users_own(auth_client, secondary_auth_client):
    """List all checkins only returns current user's checkins"""

    with allure.step("Primary user creates checkins"):
        task1 = create_task(auth_client, title="Primary task")
        primary_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task1['id'],
            note="Primary checkin"
        )

    with allure.step("Secondary user creates checkins"):
        task2 = create_task(secondary_auth_client, title="Secondary task")
        secondary_checkin = create_checkin(
            secondary_auth_client,
            target_type="task",
            target_id=task2['id'],
            note="Secondary checkin"
        )

    with allure.step("Primary user lists all checkins"):
        response = auth_client.get('/api/checkins')
        primary_checkins = response.json

    with allure.step("Verify isolation"):
        primary_ids = [c['id'] for c in primary_checkins]
        assert primary_checkin['id'] in primary_ids
        assert secondary_checkin['id'] not in primary_ids


@allure.feature('Checkins')
@allure.story('List All Checkins')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_all_checkins_with_start_date(auth_client):
    """List all checkins with start_date filter"""

    with allure.step("Create checkins with different dates"):
        task = create_task(auth_client, title="Task for date filter")
        now = datetime.now(timezone.utc)

        old_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Old checkin",
            occurred_at=(now - timedelta(days=10)).isoformat()
        )

        recent_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Recent checkin",
            occurred_at=(now - timedelta(days=2)).isoformat()
        )

    with allure.step("List all checkins with start_date filter"):
        start_date = (now - timedelta(days=5)).strftime('%Y-%m-%d')
        response = auth_client.get(f'/api/checkins?start_date={start_date}')
        checkins = response.json

    with allure.step("Verify only recent checkin returned"):
        checkin_ids = [c['id'] for c in checkins]
        assert recent_checkin['id'] in checkin_ids
        assert old_checkin['id'] not in checkin_ids


@allure.feature('Checkins')
@allure.story('List All Checkins')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_all_checkins_with_end_date(auth_client):
    """List all checkins with end_date filter"""

    with allure.step("Create checkins with different dates"):
        task = create_task(auth_client, title="Task for end date filter")
        now = datetime.now(timezone.utc)

        old_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Old checkin",
            occurred_at=(now - timedelta(days=10)).isoformat()
        )

        recent_checkin = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Recent checkin",
            occurred_at=(now - timedelta(days=2)).isoformat()
        )

    with allure.step("List all checkins with end_date filter"):
        end_date = (now - timedelta(days=5)).strftime('%Y-%m-%d')
        response = auth_client.get(f'/api/checkins?end_date={end_date}')
        checkins = response.json

    with allure.step("Verify only old checkin returned"):
        checkin_ids = [c['id'] for c in checkins]
        assert old_checkin['id'] in checkin_ids
        assert recent_checkin['id'] not in checkin_ids


@allure.feature('Checkins')
@allure.story('List All Checkins')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_all_checkins_with_date_range(auth_client):
    """List all checkins with both start_date and end_date"""

    with allure.step("Create checkins across different dates"):
        task = create_task(auth_client, title="Task for date range")
        now = datetime.now(timezone.utc)

        too_old = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Too old",
            occurred_at=(now - timedelta(days=15)).isoformat()
        )

        in_range = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="In range",
            occurred_at=(now - timedelta(days=7)).isoformat()
        )

        too_recent = create_checkin(
            auth_client,
            target_type="task",
            target_id=task['id'],
            note="Too recent",
            occurred_at=(now - timedelta(days=2)).isoformat()
        )

    with allure.step("List all checkins with date range"):
        start_date = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = (now - timedelta(days=5)).strftime('%Y-%m-%d')
        response = auth_client.get(
            f'/api/checkins?start_date={start_date}&end_date={end_date}'
        )
        checkins = response.json

    with allure.step("Verify only in-range checkin returned"):
        checkin_ids = [c['id'] for c in checkins]
        assert in_range['id'] in checkin_ids
        assert too_old['id'] not in checkin_ids
        assert too_recent['id'] not in checkin_ids


@allure.feature('Checkins')
@allure.story('List All Checkins')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_all_checkins_returns_empty_for_new_user(auth_client):
    """List all checkins returns empty array for user with no checkins"""

    with allure.step("List all checkins without creating any"):
        response = auth_client.get('/api/checkins')
        checkins = response.json

    with allure.step("Verify empty array returned"):
        assert isinstance(checkins, list)
        assert len(checkins) == 0


@allure.feature('Checkins')
@allure.story('List All Checkins')
@pytest.mark.checkins
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_all_checkins_with_pagination(auth_client):
    """List all checkins supports limit and offset"""

    with allure.step("Create multiple checkins"):
        task = create_task(auth_client, title="Task for pagination")
        for i in range(15):
            create_checkin(
                auth_client,
                target_type="task",
                target_id=task['id'],
                note=f"Checkin {i + 1}"
            )

    with allure.step("List with limit"):
        response = auth_client.get('/api/checkins?limit=10')
        limited = response.json
        assert len(limited) == 10

    with allure.step("List with offset"):
        response = auth_client.get('/api/checkins?offset=10')
        offset = response.json
        assert len(offset) >= 5