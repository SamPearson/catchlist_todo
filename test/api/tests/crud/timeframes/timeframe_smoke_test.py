import pytest
import allure
from datetime import datetime


@allure.feature('Timeframes')
@allure.story('Utility Endpoints')
@pytest.mark.timeframes
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_timeframe_kinds(auth_client):
    """List all supported timeframe kinds"""
    with allure.step("Request timeframe kinds"):
        response = auth_client.get('/api/timeframes/kinds')

    with allure.step("Verify response structure"):
        assert 'kinds' in response
        assert 'default_tz' in response
        assert isinstance(response['kinds'], list)
        assert isinstance(response['default_tz'], str)

    with allure.step("Verify all supported kinds are present"):
        kinds = response['kinds']
        assert 'day' in kinds
        assert 'week' in kinds
        assert 'month' in kinds
        assert 'season' in kinds
        assert 'year' in kinds

    with allure.step("Verify default timezone"):
        assert response['default_tz'] == 'UTC'


@allure.feature('Timeframes')
@allure.story('CRUD Operations')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_create_timeframe(auth_client):
    """Create timeframe with only kind (defaults to today)"""
    with allure.step("Prepare test data"):
        data = {"kind": "day"}

    with allure.step("Create new timeframe"):
        response = auth_client.post('/api/timeframes', data)

    with allure.step("Verify response structure and values"):
        # Response contains ID and user_id
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['user_id']
        assert isinstance(response['user_id'], int)

        # Kind matches input
        assert response['kind'] == data['kind']
        assert isinstance(response['kind'], str)

        # Timestamps present and are valid ISO format
        assert response['start_at']
        assert response['end_at']
        assert response['created_at']
        assert response['updated_at']
        assert isinstance(response['start_at'], str)
        assert isinstance(response['end_at'], str)
        assert isinstance(response['created_at'], str)
        assert isinstance(response['updated_at'], str)
        
        # Verify timestamps are parseable as ISO format
        datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))
        datetime.fromisoformat(response['created_at'].replace('Z', '+00:00'))
        datetime.fromisoformat(response['updated_at'].replace('Z', '+00:00'))

        # Label present
        assert response['label']
        assert isinstance(response['label'], str)


@allure.feature('Timeframes')
@allure.story('CRUD Operations')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_list_timeframes(auth_client):
    """Retrieve all timeframes for authenticated user"""
    with allure.step("Create multiple test timeframes"):
        created_ids = []
        for kind in ['day', 'week', 'month']:
            tf = auth_client.post('/api/timeframes', {"kind": kind})
            created_ids.append(tf['id'])

    with allure.step("Retrieve all timeframes"):
        response = auth_client.get('/api/timeframes')

    with allure.step("Verify response structure"):
        assert isinstance(response, list)
        assert len(response) >= 3

        # Verify each timeframe has required fields
        for tf in response:
            assert tf['id']
            assert tf['user_id']
            assert tf['kind']
            assert tf['start_at']
            assert tf['end_at']
            assert tf['label']
            assert 'created_at' in tf
            assert 'updated_at' in tf
            
            # Verify timestamps are valid
            datetime.fromisoformat(tf['start_at'].replace('Z', '+00:00'))
            datetime.fromisoformat(tf['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify created timeframes are in list"):
        retrieved_ids = [tf['id'] for tf in response]
        for created_id in created_ids:
            assert created_id in retrieved_ids


@allure.feature('Timeframes')
@allure.story('CRUD Operations')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_timeframe_by_id(auth_client):
    """Retrieve a specific timeframe by ID"""
    with allure.step("Create test timeframe"):
        created = auth_client.post('/api/timeframes', {
            "kind": "week",
            "date": "2025-06-08"
        })
        timeframe_id = created['id']

    with allure.step("Retrieve the timeframe"):
        retrieved = auth_client.get(f'/api/timeframes/{timeframe_id}')

    with allure.step("Verify retrieved timeframe matches created timeframe"):
        assert retrieved['id'] == timeframe_id
        assert retrieved['user_id'] == created['user_id']
        assert retrieved['kind'] == created['kind']
        assert retrieved['start_at'] == created['start_at']
        assert retrieved['end_at'] == created['end_at']
        assert retrieved['label'] == created['label']
        assert retrieved['created_at'] == created['created_at']
        assert retrieved['updated_at'] == created['updated_at']


@allure.feature('Timeframes')
@allure.story('Convenience Endpoints')
@pytest.mark.timeframes
@pytest.mark.crud
@pytest.mark.smoke_test
@allure.severity(allure.severity_level.CRITICAL)
def test_get_timeframe_for_today(auth_client):
    """Get timeframe for today via convenience endpoint"""
    with allure.step("Request day timeframe for today"):
        response = auth_client.get('/api/timeframes/day')

    with allure.step("Verify response structure"):
        assert response['id']
        assert isinstance(response['id'], int)
        assert response['kind'] == 'day'
        assert response['user_id']
        assert response['start_at']
        assert response['end_at']
        assert response['label']
        assert response['created_at']
        assert response['updated_at']
        
        # Verify timestamps are valid ISO format
        datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify get-or-create behavior - calling again returns same timeframe"):
        second_response = auth_client.get('/api/timeframes/day')
        assert second_response['id'] == response['id']
        assert second_response['start_at'] == response['start_at']
        assert second_response['end_at'] == response['end_at']