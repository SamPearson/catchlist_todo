import pytest
import allure
from datetime import date
from utils.data_factories.entity_factory import create_task


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_plan_only(auth_client):
    """Update report plan only, verify other fields unchanged"""

    with allure.step("Create report with initial data"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        # Set initial values
        auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'Initial plan',
            'reason': 'Initial reason',
            'pre_notes': 'Initial pre notes',
            'post_notes': 'Initial post notes'
        })

    with allure.step("Update only plan"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'Updated plan'
        })

    with allure.step("Verify plan changed and other fields unchanged"):
        assert response.status_code == 200
        assert response['plan'] == 'Updated plan'
        assert response['reason'] == 'Initial reason'
        assert response['pre_notes'] == 'Initial pre notes'
        assert response['post_notes'] == 'Initial post notes'


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_reason_only(auth_client):
    """Update report reason only, verify other fields unchanged"""

    with allure.step("Create report with initial data"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        # Set initial values
        auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'Initial plan',
            'reason': 'Initial reason',
            'pre_notes': 'Initial pre notes'
        })

    with allure.step("Update only reason"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'reason': 'Updated reason'
        })

    with allure.step("Verify reason changed and other fields unchanged"):
        assert response.status_code == 200
        assert response['reason'] == 'Updated reason'
        assert response['plan'] == 'Initial plan'
        assert response['pre_notes'] == 'Initial pre notes'


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_pre_notes_only(auth_client):
    """Update report pre_notes only, verify other fields unchanged"""

    with allure.step("Create report with initial data"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        # Set initial values
        auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'Initial plan',
            'pre_notes': 'Initial pre notes',
            'post_notes': 'Initial post notes'
        })

    with allure.step("Update only pre_notes"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'pre_notes': 'Updated pre notes'
        })

    with allure.step("Verify pre_notes changed and other fields unchanged"):
        assert response.status_code == 200
        assert response['pre_notes'] == 'Updated pre notes'
        assert response['plan'] == 'Initial plan'
        assert response['post_notes'] == 'Initial post notes'


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_post_notes_only(auth_client):
    """Update report post_notes only, verify other fields unchanged"""

    with allure.step("Create report with initial data"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        # Set initial values
        auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'Initial plan',
            'pre_notes': 'Initial pre notes',
            'post_notes': 'Initial post notes'
        })

    with allure.step("Update only post_notes"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'post_notes': 'Updated post notes'
        })

    with allure.step("Verify post_notes changed and other fields unchanged"):
        assert response.status_code == 200
        assert response['post_notes'] == 'Updated post notes'
        assert response['plan'] == 'Initial plan'
        assert response['pre_notes'] == 'Initial pre notes'


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_all_text_fields_together(auth_client):
    """Update all text fields together, verify all change"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Update all text fields"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'New plan',
            'reason': 'New reason',
            'pre_notes': 'New pre notes',
            'post_notes': 'New post notes'
        })

    with allure.step("Verify all fields updated"):
        assert response.status_code == 200
        assert response['plan'] == 'New plan'
        assert response['reason'] == 'New reason'
        assert response['pre_notes'] == 'New pre notes'
        assert response['post_notes'] == 'New post notes'


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_with_empty_plan(auth_client):
    """Update report with empty plan clears the field"""

    with allure.step("Create report with plan"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        auth_client.put(f'/api/reports/{report_id}', data={
            'plan': 'Initial plan'
        })

    with allure.step("Clear plan with empty string"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'plan': ''
        })

    with allure.step("Verify plan cleared"):
        assert response.status_code == 200
        assert response['plan'] == '' or response['plan'] is None


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_with_empty_reason(auth_client):
    """Update report with empty reason clears the field"""

    with allure.step("Create report with reason"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        auth_client.put(f'/api/reports/{report_id}', data={
            'reason': 'Initial reason'
        })

    with allure.step("Clear reason with empty string"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'reason': ''
        })

    with allure.step("Verify reason cleared"):
        assert response.status_code == 200
        assert response['reason'] == '' or response['reason'] is None


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_with_empty_pre_notes(auth_client):
    """Update report with empty pre_notes clears the field"""

    with allure.step("Create report with pre_notes"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        auth_client.put(f'/api/reports/{report_id}', data={
            'pre_notes': 'Initial pre notes'
        })

    with allure.step("Clear pre_notes with empty string"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'pre_notes': ''
        })

    with allure.step("Verify pre_notes cleared"):
        assert response.status_code == 200
        assert response['pre_notes'] == '' or response['pre_notes'] is None


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_with_empty_post_notes(auth_client):
    """Update report with empty post_notes clears the field"""

    with allure.step("Create report with post_notes"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

        auth_client.put(f'/api/reports/{report_id}', data={
            'post_notes': 'Initial post notes'
        })

    with allure.step("Clear post_notes with empty string"):
        response = auth_client.put(f'/api/reports/{report_id}', data={
            'post_notes': ''
        })

    with allure.step("Verify post_notes cleared"):
        assert response.status_code == 200
        assert response['post_notes'] == '' or response['post_notes'] is None


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_with_no_data(auth_client):
    """Update report with no data returns 400 error"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Attempt to update with no data"):
        response = auth_client.put(f'/api/reports/{report_id}', data={}, handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_with_empty_request_body(auth_client):
    """Update report with empty request body returns 400 error"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Attempt to update with empty body"):
        response = auth_client.put(f'/api/reports/{report_id}', data=None, handle_response=False)

    with allure.step("Verify 415 error"):
        assert response.status_code == 415



@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_report_with_full_true(auth_client):
    """Update report with full=true includes metadata in response"""

    with allure.step("Create report"):
        today = date.today().isoformat()
        created = auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        report_id = created['id']

    with allure.step("Update report with full=true"):
        response = auth_client.put(f'/api/reports/{report_id}',
                                   data={'plan': 'Updated plan'},
                                   params={'full': True}
                                   )

    with allure.step("Verify metadata included in response"):
        assert response.status_code == 200
        assert response['plan'] == 'Updated plan'
        assert 'id' in response
        assert 'user_id' in response
        assert 'timeframe_id' in response
        assert 'created_at' in response
        assert 'updated_at' in response


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_nonexistent_report(auth_client):
    """Update nonexistent report returns 404"""

    with allure.step("Attempt to update nonexistent report"):
        response = auth_client.put('/api/reports/999999',
                                   data={'plan': 'Updated plan'},
                                   handle_response=False
                                   )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404


@allure.feature('Reports')
@allure.story('Update Report')
@pytest.mark.reports
@pytest.mark.update
@allure.severity(allure.severity_level.NORMAL)
def test_update_another_users_report(auth_client, secondary_auth_client):
    """Update another user's report returns 404"""

    with allure.step("Secondary user creates report"):
        today = date.today().isoformat()
        secondary_report = secondary_auth_client.get(f'/api/reports/day/{today}', params={'full': True})
        secondary_report_id = secondary_report['id']

    with allure.step("Primary user attempts to update secondary user's report"):
        response = auth_client.put(f'/api/reports/{secondary_report_id}',
                                   data={'plan': 'Trying to update'},
                                   handle_response=False
                                   )

    with allure.step("Verify 404 error"):
        assert response.status_code == 404