import pytest
import allure


@allure.feature('Backup')
@allure.story('Export')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_export_requires_auth(unauthenticated_client):
    """Export endpoint requires a valid JWT"""

    with allure.step("Export without auth token"):
        response = unauthenticated_client.get('/api/backup/export', handle_response=False)

    with allure.step("Verify 422 from missing auth header"):
        assert response.status_code == 422


@allure.feature('Backup')
@allure.story('Export')
@pytest.mark.backup
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_export_empty_user_returns_valid_envelope(auth_client):
    """Export for a brand new user returns the full envelope with empty lists"""

    with allure.step("Export empty user data"):
        response = auth_client.get('/api/backup/export')

    with allure.step("Verify envelope structure"):
        assert response['format'] == 'catchlist-backup'
        assert response['version'] == 1
        assert 'exported_at' in response

    with allure.step("Verify user profile present without credentials"):
        assert response['user']['username']
        assert 'password_hash' not in response['user']
        assert 'password' not in response['user']

    with allure.step("Verify all entity collections are empty lists"):
        for key in [
            'tags', 'principles', 'projects', 'tasks', 'calendars', 'routines',
            'sessions', 'timeframes', 'reports', 'commitments', 'checkins',
            'tag_associations', 'principle_associations'
        ]:
            assert key in response
            assert isinstance(response[key], list)
            assert response[key] == []


@allure.feature('Backup')
@allure.story('Export')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_export_contains_created_entities(auth_client):
    """Export includes every entity the user created"""

    with allure.step("Create a project and a task inside it"):
        project = auth_client.post('/api/projects', {"title": "Export Project"})
        project_id = project['id']
        task = auth_client.post('/api/tasks', {
            "title": "Export Task",
            "project_id": project_id
        })
        task_id = task['id']

    with allure.step("Create a tag and attach it to the task"):
        tag = auth_client.post('/api/tags', {"name": "important"})
        tag_id = tag['id']
        attach = auth_client.post('/api/tags/attach', {
            "tag_id": tag_id,
            "target_type": "task",
            "target_id": task_id
        })
        assert attach['success'] is True

    with allure.step("Create a calendar, routine and session"):
        calendar = auth_client.post('/api/calendars', {"name": "Export Calendar"})
        calendar_id = calendar['id']
        routine = auth_client.post('/api/routines', {
            "title": "Export Routine",
            "calendar_id": calendar_id
        })
        routine_id = routine['id']
        auth_client.post(f'/api/routines/{routine_id}/sessions', {
            "start_time": "2025-06-08T09:00:00",
            "end_time": "2025-06-08T10:00:00"
        })

    with allure.step("Create a timeframe, report and commitment"):
        timeframe = auth_client.post('/api/timeframes', {"kind": "day"})
        timeframe_id = timeframe['id']
        auth_client.get(f'/api/reports/day/2025-06-08')
        auth_client.post('/api/commitments/soft', {
            "target_type": "task",
            "target_id": task_id,
            "timeframe_id": timeframe_id
        })

    with allure.step("Create a checkin"):
        auth_client.post('/api/checkins', {
            "target_type": "task",
            "target_id": task_id,
            "note": "Export checkin"
        })

    with allure.step("Export the data"):
        response = auth_client.get('/api/backup/export')

    with allure.step("Verify projects and tasks present"):
        assert len(response['projects']) == 1
        assert response['projects'][0]['title'] == 'Export Project'
        assert len(response['tasks']) == 1
        assert response['tasks'][0]['title'] == 'Export Task'
        assert response['tasks'][0]['project_id'] == project_id

    with allure.step("Verify tags and their association present"):
        assert len(response['tags']) == 1
        assert response['tags'][0]['name'] == 'important'
        assert response['tag_associations'] == [{
            'tag_id': tag_id,
            'entity_id': task_id,
            'entity_type': 'task'
        }]

    with allure.step("Verify calendars, routines and sessions present"):
        assert len(response['calendars']) == 1
        assert response['calendars'][0]['name'] == 'Export Calendar'
        assert len(response['routines']) == 1
        assert response['routines'][0]['title'] == 'Export Routine'
        assert response['routines'][0]['calendar_id'] == calendar_id
        assert len(response['sessions']) == 1
        assert response['sessions'][0]['routine_id'] == routine_id

    with allure.step("Verify timeframes, reports and commitments present"):
        assert len(response['timeframes']) >= 1
        assert len(response['reports']) >= 1
        task_commitments = [
            c for c in response['commitments']
            if c['target_type'] == 'task' and c['target_id'] == task_id
        ]
        assert task_commitments, "No task commitment exported"

    with allure.step("Verify checkins present"):
        assert len(response['checkins']) == 1
        assert response['checkins'][0]['target_type'] == 'task'
        assert response['checkins'][0]['note'] == 'Export checkin'


@allure.feature('Backup')
@allure.story('Export')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_export_isolates_users(auth_client, secondary_auth_client):
    """Export only returns the current user's data, never another user's"""

    with allure.step("Secondary user creates a task"):
        secondary_auth_client.post('/api/tasks', {
            "title": "Secret Secondary Task"
        })

    with allure.step("Primary user exports"):
        response = auth_client.get('/api/backup/export')

    with allure.step("Verify primary user has no tasks"):
        assert response['tasks'] == []


@allure.feature('Backup')
@allure.story('Export')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_export_never_exports_password_hash(auth_client):
    """Export profile must never contain password material"""

    with allure.step("Export user data"):
        response = auth_client.get('/api/backup/export')

    with allure.step("Verify no password fields leak"):
        user = response['user']
        for key in ('password', 'password_hash', '_password_hash', 'hash'):
            assert key not in user

    with allure.step("Verify serialized rows contain no user_id column"):
        for key in response.json:
            if isinstance(response.json[key], list) and response.json[key] and isinstance(response.json[key][0], dict):
                assert 'user_id' not in response.json[key][0], \
                    f"Backup '{key}' leaked user_id"