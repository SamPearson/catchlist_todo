import pytest
import allure


@allure.feature('Timeframes')
@allure.story('Multi-User Isolation')
@pytest.mark.timeframes
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_users_cannot_access_each_others_timeframes_by_id(auth_client, secondary_auth_client):
    """Users cannot access each other's timeframes by ID"""
    with allure.step("Create timeframe as primary user"):
        user1_timeframe = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08"
        })
        user1_id = user1_timeframe['id']

    with allure.step("Create timeframe as secondary user"):
        user2_timeframe = secondary_auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08"
        })
        user2_id = user2_timeframe['id']

    with allure.step("Primary user attempts to access secondary user's timeframe"):
        response = auth_client.get(f'/api/timeframes/{user2_id}',
                                   handle_response=False)

    with allure.step("Verify 404 (acts as if doesn't exist)"):
        assert response.status_code == 404

    with allure.step("Secondary user attempts to access primary user's timeframe"):
        response = secondary_auth_client.get(f'/api/timeframes/{user1_id}',
                                             handle_response=False)

    with allure.step("Verify 404 (acts as if doesn't exist)"):
        assert response.status_code == 404


@allure.feature('Timeframes')
@allure.story('Multi-User Isolation')
@pytest.mark.timeframes
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_users_can_create_identical_timeframes_independently(auth_client, secondary_auth_client):
    """Users can create identical timeframes independently"""
    with allure.step("Primary user creates day timeframe for June 8"):
        user1_timeframe = auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08"
        })
        user1_id = user1_timeframe['id']

    with allure.step("Secondary user creates day timeframe for same date"):
        user2_timeframe = secondary_auth_client.post('/api/timeframes', {
            "kind": "day",
            "date": "2025-06-08"
        })
        user2_id = user2_timeframe['id']

    with allure.step("Verify separate timeframe records created"):
        assert user1_id != user2_id

    with allure.step("Verify both have same kind and boundaries"):
        assert user1_timeframe['kind'] == user2_timeframe['kind']
        assert user1_timeframe['start_at'] == user2_timeframe['start_at']
        assert user1_timeframe['end_at'] == user2_timeframe['end_at']

    with allure.step("Verify different user_id"):
        assert user1_timeframe['user_id'] != user2_timeframe['user_id']


@allure.feature('Timeframes')
@allure.story('Multi-User Isolation')
@pytest.mark.timeframes
@pytest.mark.multi_user
@allure.severity(allure.severity_level.NORMAL)
def test_list_timeframes_only_shows_own_timeframes(auth_client, secondary_auth_client):
    """List timeframes only shows authenticated user's own timeframes"""
    with allure.step("Primary user creates multiple timeframes"):
        user1_tf1 = auth_client.post('/api/timeframes', {"kind": "day"})
        user1_tf2 = auth_client.post('/api/timeframes', {"kind": "week"})
        user1_ids = [user1_tf1['id'], user1_tf2['id']]

    with allure.step("Secondary user creates multiple timeframes"):
        user2_tf1 = secondary_auth_client.post('/api/timeframes', {"kind": "day"})
        user2_tf2 = secondary_auth_client.post('/api/timeframes', {"kind": "month"})
        user2_ids = [user2_tf1['id'], user2_tf2['id']]

    with allure.step("Primary user lists their timeframes"):
        user1_list = auth_client.get('/api/timeframes')
        user1_list_ids = [tf['id'] for tf in user1_list]

    with allure.step("Secondary user lists their timeframes"):
        user2_list = secondary_auth_client.get('/api/timeframes')
        user2_list_ids = [tf['id'] for tf in user2_list]

    with allure.step("Verify primary user only sees their own timeframes"):
        for tf_id in user1_ids:
            assert tf_id in user1_list_ids
        for tf_id in user2_ids:
            assert tf_id not in user1_list_ids

    with allure.step("Verify secondary user only sees their own timeframes"):
        for tf_id in user2_ids:
            assert tf_id in user2_list_ids
        for tf_id in user1_ids:
            assert tf_id not in user2_list_ids