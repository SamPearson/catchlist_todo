import pytest
import allure


def _build_simple_blob(**overrides):
    """Build a minimal valid backup blob for import tests."""
    blob = {
        "format": "catchlist-backup",
        "version": 1,
        "exported_at": "2026-01-01T00:00:00",
        "user": {
            "username": "anyuser",
            "name": "Imported User",
            "timezone": "UTC"
        },
        "tags": [],
        "principles": [],
        "projects": [],
        "tasks": [],
        "calendars": [],
        "routines": [],
        "sessions": [],
        "timeframes": [],
        "reports": [],
        "commitments": [],
        "checkins": [],
        "tag_associations": [],
        "principle_associations": []
    }
    blob.update(overrides)
    return blob


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_import_requires_auth(unauthenticated_client):
    """Import endpoint requires a valid JWT"""

    with allure.step("Import without auth token"):
        response = unauthenticated_client.post('/api/backup/import', {
            "password": "whatever",
            "data": _build_simple_blob()
        }, handle_response=False)

    with allure.step("Verify 422 from missing auth header"):
        assert response.status_code == 422


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_import_requires_password(auth_client):
    """Import refuses to run without the account password"""

    with allure.step("Import without password"):
        response = auth_client.post('/api/backup/import', {
            "data": _build_simple_blob()
        }, handle_response=False)

    with allure.step("Verify 400 with message"):
        assert response.status_code == 400
        assert response.json['message'] == 'Password required for backup restore'


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_import_rejects_wrong_password(auth_client):
    """Import refuses to run with an incorrect password"""

    with allure.step("Import with wrong password"):
        response = auth_client.post('/api/backup/import', {
            "password": "not-the-password",
            "data": _build_simple_blob()
        }, handle_response=False)

    with allure.step("Verify 401 with message"):
        assert response.status_code == 401
        assert response.json['message'] == 'Invalid password'


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_import_requires_data(auth_client):
    """Import requires a data blob in the payload"""

    with allure.step("Import without data"):
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password
        }, handle_response=False)

    with allure.step("Verify 400 with message"):
        assert response.status_code == 400
        assert response.json['message'] == 'Backup data is required'


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_import_rejects_invalid_format(auth_client):
    """Import rejects a blob with an unknown format"""

    with allure.step("Import blob with wrong format"):
        blob = _build_simple_blob(format="not-a-backup")
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password,
            "data": blob
        }, handle_response=False)

    with allure.step("Verify 400 with error message"):
        assert response.status_code == 400
        assert response.json['error'] == "Unsupported backup format: 'not-a-backup'"


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_import_rejects_invalid_version(auth_client):
    """Import rejects a blob with an unsupported version"""

    with allure.step("Import blob with future version"):
        blob = _build_simple_blob(version=99)
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password,
            "data": blob
        }, handle_response=False)

    with allure.step("Verify 400 with error message"):
        assert response.status_code == 400
        assert response.json['error'] == 'Unsupported backup version: 99'


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_import_does_not_overwrite_username(auth_client):
    """Import never changes the account username, only display name/timezone"""

    with allure.step("Import a blob carrying a different username"):
        blob = _build_simple_blob(
            user={"username": "someone-else", "name": "Blob Name", "timezone": "UTC"}
        )
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password,
            "data": blob
        })

    with allure.step("Verify import succeeded"):
        assert response.status_code == 200

    with allure.step("Verify username is untouched while profile updated"):
        info = auth_client.get('/api/auth/user-info')
        assert info['username'] == auth_client.current_user.username
        assert info['name'] == 'Blob Name'
        assert info['timezone'] == 'UTC'


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_import_creates_entities_from_blob(auth_client):
    """Importing a blob creates the described entities"""

    with allure.step("Build a blob with a task and a tag"):
        blob = _build_simple_blob(
            user={"username": auth_client.current_user.username,
                  "name": "Round Trip User",
                  "timezone": "UTC"},
            tags=[{"name": "restored-tag"}],
            tasks=[{"title": "Restored Task"}]
        )

    with allure.step("Import the blob"):
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password,
            "data": blob
        }, handle_response=True)

    with allure.step("Verify import succeeded"):
        assert response.status_code == 200

    with allure.step("Verify the task exists via the API"):
        tasks = auth_client.get('/api/tasks?include_completed=true').json
        assert any(t['title'] == 'Restored Task' for t in tasks)

    with allure.step("Verify the tag exists via the API"):
        tags = auth_client.get('/api/tags').json
        assert any(t['name'] == 'restored-tag' for t in tags)

    with allure.step("Verify profile name and timezone were applied"):
        info = auth_client.get('/api/auth/user-info')
        assert info['name'] == 'Round Trip User'
        assert info['timezone'] == 'UTC'


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_import_preserves_relationships(auth_client):
    """Import remaps foreign keys so relationships survive the restore"""

    with allure.step("Build a blob with project->task, calendar->routine->session, tag association"):
        blob = _build_simple_blob(
            user={"username": auth_client.current_user.username,
                  "name": None,
                  "timezone": "UTC"},
            tags=[
                {"id": 101, "name": "rel-tag"}
            ],
            projects=[
                {"id": 201, "title": "Rel Project"}
            ],
            tasks=[
                {"id": 301, "title": "Rel Task", "project_id": 201}
            ],
            calendars=[
                {"id": 401, "name": "Rel Calendar"}
            ],
            routines=[
                {"id": 501, "title": "Rel Routine", "calendar_id": 401}
            ],
            sessions=[
                {"id": 601, "routine_id": 501,
                 "start_time": "2026-01-01T09:00:00",
                 "end_time": "2026-01-01T10:00:00"}
            ],
            tag_associations=[
                {"tag_id": 101, "entity_id": 301, "entity_type": "task"}
            ]
        )

    with allure.step("Import the blob"):
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password,
            "data": blob
        })

    with allure.step("Verify import succeeded"):
        assert response.status_code == 200

    with allure.step("Verify the task belongs to the project"):
        tasks = auth_client.get('/api/tasks?include_completed=true').json
        task = next(t for t in tasks if t['title'] == 'Rel Task')
        projects = auth_client.get('/api/projects').json
        project = next(p for p in projects if p['title'] == 'Rel Project')
        assert task['project_id'] == project['id']

    with allure.step("Verify the routine belongs to the calendar"):
        routines = auth_client.get('/api/routines').json
        routine = next(r for r in routines if r['title'] == 'Rel Routine')
        calendars = auth_client.get('/api/calendars').json
        calendar = next(c for c in calendars if c['name'] == 'Rel Calendar')
        assert routine['calendar_id'] == calendar['id']

    with allure.step("Verify the session belongs to the routine"):
        sessions = auth_client.get(
            '/api/sessions?start=2026-01-01T00:00:00&end=2026-01-05T00:00:00').json
        assert any(s['routine_id'] == routine['id'] for s in sessions)

    with allure.step("Verify the tag association is attached to the task"):
        task_with_tag = auth_client.get(f'/api/tasks/{task["id"]}')
        assert 'tags' in task_with_tag
        tag_ids = [t['id'] for t in task_with_tag['tags']]
        assert len(tag_ids) == 1


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.CRITICAL)
def test_import_full_replace_clears_old_data(auth_client):
    """Import is a full replace: data not in the blob is removed"""

    with allure.step("Crate a pre-existing task"):
        auth_client.post('/api/tasks', {"title": "Old Task To Be Wiped"})

    with allure.step("Import a blob that only contains a new task"):
        blob = _build_simple_blob(
            user={"username": auth_client.current_user.username,
                  "name": None,
                  "timezone": "UTC"},
            tasks=[{"id": 701, "title": "New Task From Blob"}]
        )
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password,
            "data": blob
        })

    with allure.step("Verify import succeeded"):
        assert response.status_code == 200

    with allure.step("Verify the old task is gone"):
        tasks = auth_client.get('/api/tasks?include_completed=true').json
        assert all(t['title'] != 'Old Task To Be Wiped' for t in tasks)
        assert any(t['title'] == 'New Task From Blob' for t in tasks)


@allure.feature('Backup')
@allure.story('Import')
@pytest.mark.backup
@pytest.mark.crud
@allure.severity(allure.severity_level.NORMAL)
def test_import_rejects_malformed_entity_lists(auth_client):
    """Import rejects blobs where an entity field is not a list"""

    with allure.step("Import blob with non-list tasks field"):
        blob = _build_simple_blob(tasks="not-a-list")
        response = auth_client.post('/api/backup/import', {
            "password": auth_client.current_user.password,
            "data": blob
        }, handle_response=False)

    with allure.step("Verify 400 with error message"):
        assert response.status_code == 400
        assert response.json['error'] == "Backup field 'tasks' must be a list."