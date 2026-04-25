import allure
from datetime import datetime, timedelta, timezone


def create_task(auth_client, **kwargs):
    """Helper to create a task with custom properties"""
    payload = {
        "title": kwargs.get("title", "Sample Task"),
        "description": kwargs.get("description", ""),
        "status": kwargs.get("status", "open"),
    }

    with allure.step(f"Create task: {payload['title']}"):
        response = auth_client.post('/api/tasks', data=payload)
        assert response.status_code == 201, f"Failed to create task: {response.text}"
        task = response.json

    return task


def create_project(auth_client, **kwargs):
    """Helper to create a project with custom properties"""
    payload = {
        "title": kwargs.get("title", "Test Project"),
        "description": kwargs.get("description", ""),
        "win_condition": kwargs.get("win_condition", ""),
        "reason": kwargs.get("reason", ""),
        "next_step": kwargs.get("next_step", ""),
    }

    with allure.step(f"Create project: {payload['title']}"):
        response = auth_client.post('/api/projects', data=payload)
        assert response.status_code == 201, f"Failed to create project: {response.text}"
        project = response.json

    return project


def create_calendar(auth_client, **kwargs):
    """Helper to create a calendar with custom properties"""
    payload = {
        "name": kwargs.get("name", "Test Calendar"),
        "color": kwargs.get("color"),
        "external_uid": kwargs.get("external_uid"),
        "external_source": kwargs.get("external_source"),
    }

    # Remove None values to allow API defaults
    payload = {k: v for k, v in payload.items() if v is not None}

    with allure.step(f"Create calendar: {payload['name']}"):
        response = auth_client.post('/api/calendars', data=payload)
        assert response.status_code == 201, f"Failed to create calendar: {response.text}"
        calendar = response.json

    return calendar


def create_routine(auth_client, **kwargs):
    """Helper to create a routine with custom properties"""
    payload = {
        "title": kwargs.get("title", "Test Routine"),
        "description": kwargs.get("description", ""),
        "rrule": kwargs.get("rrule"),
        "start_time": kwargs.get("start_time"),
        "end_time": kwargs.get("end_time"),
        "calendar_id": kwargs.get("calendar_id"),
        "active": kwargs.get("active"),
    }

    # Remove None values to allow API defaults
    payload = {k: v for k, v in payload.items() if v is not None}

    with allure.step(f"Create routine: {payload['title']}"):
        response = auth_client.post('/api/routines', data=payload)
        assert response.status_code == 201, f"Failed to create routine: {response.text}"
        routine = response.json

    return routine


def create_session(auth_client, routine_id, **kwargs):
    """Helper to create a session for a routine with custom properties

    Args:
        auth_client: Authenticated API client
        routine_id: ID of the routine this session belongs to
        **kwargs: Optional session properties (start_time, end_time, status, notes, rpe)
    """
    # Default to now + 1 hour for start/end times if not provided
    default_start = datetime.now(timezone.utc)
    default_end = default_start + timedelta(hours=1)

    payload = {
        "start_time": kwargs.get("start_time", default_start.isoformat()),
        "end_time": kwargs.get("end_time", default_end.isoformat()),
        "status": kwargs.get("status", "scheduled"),
        "notes": kwargs.get("notes", ""),
        "rpe": kwargs.get("rpe"),
    }

    # Remove None values to allow API defaults
    payload = {k: v for k, v in payload.items() if v is not None}

    with allure.step(f"Create session for routine {routine_id}"):
        response = auth_client.post(f'/api/routines/{routine_id}/sessions', data=payload)
        assert response.status_code == 201, f"Failed to create session: {response.text}"
        session = response.json

    return session


def create_timeframe(auth_client, **kwargs):
    """Helper to create a timeframe with custom properties

    Args:
        auth_client: Authenticated API client
        **kwargs: Optional timeframe properties (kind, date, tz)
                 kind options: 'day', 'week', 'month', 'season', 'year'
    """
    payload = {
        "kind": kwargs.get("kind", "day"),
        "date": kwargs.get("date"),
        "tz": kwargs.get("tz"),
    }

    # Remove None values to allow API defaults
    payload = {k: v for k, v in payload.items() if v is not None}

    with allure.step(f"Create timeframe: {payload['kind']}"):
        response = auth_client.post('/api/timeframes', data=payload)
        assert response.status_code == 201, f"Failed to create timeframe: {response.text}"
        timeframe = response.json

    return timeframe


def create_report(auth_client, kind, date, **kwargs):
    """Helper to create a report with custom properties

    Args:
        auth_client: Authenticated API client
        kind: Timeframe kind - one of: 'day', 'week', 'month', 'season', 'year'
        date: ISO date string (YYYY-MM-DD)
        **kwargs: Optional report properties (timezone, plan, reason, pre_notes, post_notes,
                  full, commitment_scope)
    """
    # First, get or create the report via the GET endpoint
    params = {}
    if "full" in kwargs:
        params["full"] = kwargs["full"]
    else:
        params["full"] = True

    if "timezone" in kwargs:
        params["timezone"] = kwargs["timezone"]
    if "commitment_scope" in kwargs:
        params["commitment_scope"] = kwargs["commitment_scope"]

    with allure.step(f"Get or create report: {kind}/{date}"):
        response = auth_client.get(f'/api/reports/{kind}/{date}', params=params)
        assert response.status_code == 200, f"Failed to get/create report: {response.text}"
        report = response.json

    # If we have text fields to update, make a PUT request
    update_fields = {}
    for field in ["plan", "reason", "pre_notes", "post_notes"]:
        if field in kwargs:
            update_fields[field] = kwargs[field]

    if update_fields:
        report_id = report.get("id")
        if not report_id:
            # If full=false, we need to fetch with full=true to get the ID
            full_response = auth_client.get(f'/api/reports/{kind}/{date}', query_string={"full": True})
            assert full_response.status_code == 200, f"Failed to get report ID: {full_response.text}"
            report_id = full_response.json["id"]

        update_params = {}
        if "full" in kwargs:
            update_params["full"] = kwargs["full"]
        if "commitment_scope" in kwargs:
            update_params["commitment_scope"] = kwargs["commitment_scope"]

        with allure.step(f"Update report {report_id} with text fields"):
            response = auth_client.put(
                f'/api/reports/{report_id}',
                data=update_fields,
                query_string=update_params if update_params else None
            )
            assert response.status_code == 200, f"Failed to update report: {response.text}"
            report = response.json

    return report

def create_checkin(auth_client, **kwargs):
    """Helper to create a checkin with custom properties

    Args:
        auth_client: Authenticated API client
        **kwargs: Checkin properties (target_type, target_id required; note, occurred_at optional)
    """
    if "target_id" not in kwargs:
        raise ValueError("target_id is required to create a checkin")

    payload = {
        "target_type": kwargs.get("target_type", "task"),
        "target_id": kwargs["target_id"],
        "note": kwargs.get("note", "Test checkin note"),
        "occurred_at": kwargs.get("occurred_at"),
    }

    # Remove None values to allow API defaults
    payload = {k: v for k, v in payload.items() if v is not None}

    with allure.step(f"Create checkin for {payload['target_type']} {payload['target_id']}"):
        response = auth_client.post('/api/checkins', data=payload)
        assert response.status_code == 201, f"Failed to create checkin: {response.text}"
        checkin = response.json

    return checkin