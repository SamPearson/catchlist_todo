import pytest
import allure


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_returns_empty_array(auth_client):
    """List timeframes returns empty array for user with no timeframes"""
    with allure.step("List timeframes for fresh user (no timeframes created yet)"):
        response = auth_client.get('/api/timeframes')

    with allure.step("Verify empty array returned"):
        assert isinstance(response, list)
        assert len(response) == 0


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_only_returns_users_own_timeframes(auth_client, secondary_auth_client):
    """List timeframes returns only the authenticated user's timeframes"""
    with allure.step("Create timeframe for first user"):
        user1_timeframe = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08"
        })
        user1_id = user1_timeframe['id']

    with allure.step("Create timeframe for second user"):
        user2_timeframe = secondary_auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08"
        })
        user2_id = user2_timeframe['id']

    with allure.step("List timeframes for first user"):
        user1_timeframes = auth_client.get('/api/timeframes')

    with allure.step("List timeframes for second user"):
        user2_timeframes = secondary_auth_client.get('/api/timeframes')

    with allure.step("Verify each user only sees their own timeframes"):
        user1_ids = [tf['id'] for tf in user1_timeframes]
        user2_ids = [tf['id'] for tf in user2_timeframes]

        assert user1_id in user1_ids
        assert user2_id not in user1_ids

        assert user2_id in user2_ids
        assert user1_id not in user2_ids


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_filters_by_kind(auth_client):
    """List timeframes with kind parameter filters results"""
    with allure.step("Create timeframes of different kinds"):
        day_tf = auth_client.post('/api/timeframes', {"kind": "day"})
        week_tf = auth_client.post('/api/timeframes', {"kind": "week"})
        month_tf = auth_client.post('/api/timeframes', {"kind": "month"})

        day_id = day_tf['id']
        week_id = week_tf['id']
        month_id = month_tf['id']

    with allure.step("List timeframes filtered by kind=day"):
        response = auth_client.get('/api/timeframes?kind=day')

    with allure.step("Verify only day timeframes returned"):
        timeframe_ids = [tf['id'] for tf in response]
        timeframe_kinds = [tf['kind'] for tf in response]

        assert day_id in timeframe_ids
        assert week_id not in timeframe_ids
        assert month_id not in timeframe_ids
        assert all(kind == 'day' for kind in timeframe_kinds)


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_invalid_kind(auth_client):
    """List timeframes with invalid kind returns 400 error"""
    with allure.step("Request timeframes with invalid kind"):
        response = auth_client.get('/api/timeframes?kind=invalid_kind',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_start_and_end_dates(auth_client):
    """List timeframes with start and end date window"""
    with allure.step("Create timeframes for different dates"):
        # Create timeframes that should be in range
        tf1 = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-10"
        })
        tf2 = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-15"
        })
        # Create timeframe outside range
        tf3 = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-07-01"
        })

        in_range_ids = [tf1['id'], tf2['id']]
        out_of_range_id = tf3['id']

    with allure.step("List timeframes with date window"):
        response = auth_client.get('/api/timeframes?kind=day&start=2025-06-01&end=2025-06-30')

    with allure.step("Verify only timeframes in range returned"):
        timeframe_ids = [tf['id'] for tf in response]

        for tf_id in in_range_ids:
            assert tf_id in timeframe_ids
        assert out_of_range_id not in timeframe_ids


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_start_and_end_requires_kind(auth_client):
    """List timeframes with start/end dates requires kind parameter"""
    with allure.step("Request timeframes with date window but no kind"):
        response = auth_client.get('/api/timeframes?start=2025-06-01&end=2025-06-30',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data
        assert 'kind is required' in error_data['error'].lower()


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_invalid_start_date_format(auth_client):
    """List timeframes with invalid start date format returns 400"""
    with allure.step("Request timeframes with invalid start date"):
        response = auth_client.get('/api/timeframes?kind=day&start=invalid&end=2025-06-30',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_invalid_end_date_format(auth_client):
    """List timeframes with invalid end date format returns 400"""
    with allure.step("Request timeframes with invalid end date"):
        response = auth_client.get('/api/timeframes?kind=day&start=2025-06-01&end=not-a-date',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_end_before_start(auth_client):
    """List timeframes with end date before start date returns 400"""
    with allure.step("Request timeframes with end before start"):
        response = auth_client.get('/api/timeframes?kind=day&start=2025-06-30&end=2025-06-01',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data
        assert 'end must be on or after start' in error_data['error'].lower()


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_invalid_timezone(auth_client):
    """List timeframes with invalid timezone returns 400"""
    with allure.step("Request timeframes with invalid timezone"):
        response = auth_client.get('/api/timeframes?tz=Invalid/Timezone',
                                   handle_response=False)

    with allure.step("Verify 400 error"):
        assert response.status_code == 400
        error_data = response.json()
        assert 'error' in error_data
        assert 'invalid timezone' in error_data['error'].lower()


@allure.feature('Timeframes')
@allure.story('List Timeframes')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.list
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_with_valid_timezone(auth_client):
    """List timeframes with valid timezone parameter"""
    with allure.step("Create a timeframe"):
        auth_client.post('/api/timeframes', {"kind": "day"})

    with allure.step("Request timeframes with valid timezone"):
        response = auth_client.get('/api/timeframes?tz=America/Chicago')

    with allure.step("Verify request succeeds"):
        assert isinstance(response, list)


@allure.feature('Timeframes')
@allure.story('Get Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_timeframe_returns_full_object(auth_client):
    """Get timeframe returns all fields"""
    with allure.step("Create test timeframe"):
        created = auth_client.post('/api/timeframes', {
            "kind": "month",
            "date": "2025-06-15"
        })
        timeframe_id = created['id']

    with allure.step("Retrieve the timeframe"):
        retrieved = auth_client.get(f'/api/timeframes/{timeframe_id}')

    with allure.step("Verify all fields present"):
        assert 'id' in retrieved
        assert 'user_id' in retrieved
        assert 'kind' in retrieved
        assert 'start_at' in retrieved
        assert 'end_at' in retrieved
        assert 'label' in retrieved
        assert 'created_at' in retrieved
        assert 'updated_at' in retrieved


@allure.feature('Timeframes')
@allure.story('Get Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_timeframe(auth_client):
    """Get nonexistent timeframe returns 404"""
    with allure.step("Request nonexistent timeframe"):
        response = auth_client.get('/api/timeframes/99999',
                                   handle_response=False)

    with allure.step("Verify 404 response"):
        assert response.status_code == 404


@allure.feature('Timeframes')
@allure.story('Get Timeframe')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.get
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_get_another_users_timeframe(auth_client, secondary_auth_client):
    """Get another user's timeframe returns 404"""
    with allure.step("Create timeframe as secondary user"):
        other_timeframe = secondary_auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08"
        })
        other_id = other_timeframe['id']

    with allure.step("Attempt to retrieve as primary user"):
        response = auth_client.get(f'/api/timeframes/{other_id}',
                                   handle_response=False)

    with allure.step("Verify 404 response (acts as if doesn't exist)"):
        assert response.status_code == 404