import pytest
import allure
from datetime import datetime


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_day_timeframe_spans_24_hours(auth_client):
    """Day timeframe spans exactly 24 hours"""
    with allure.step("Create day timeframe"):
        response = auth_client.get('/api/timeframes/day/2025-06-08')

    with allure.step("Parse timestamps"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify 24 hour span"):
        duration = end - start
        assert duration.total_seconds() == 86400  # 24 hours = 86400 seconds


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_day_timeframe_label_format(auth_client):
    """Day timeframe label matches YYYY-MM-DD format"""
    with allure.step("Create day timeframe"):
        response = auth_client.get('/api/timeframes/day/2025-06-08')

    with allure.step("Verify label format"):
        assert response['label'] == '2025-06-08'


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_week_timeframe_starts_on_sunday(auth_client):
    """Week timeframe starts on Sunday"""
    with allure.step("Create week timeframe for date in middle of week"):
        # June 8, 2025 is a Sunday, so week should start on June 8
        response = auth_client.get('/api/timeframes/week/2025-06-08')

    with allure.step("Parse start timestamp"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))

    with allure.step("Verify start is Sunday (weekday 6)"):
        assert start.weekday() == 6  # Sunday = 6 in Python's weekday()


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_week_timeframe_ends_on_sunday(auth_client):
    """Week timeframe ends on following Sunday"""
    with allure.step("Create week timeframe"):
        response = auth_client.get('/api/timeframes/week/2025-06-10')

    with allure.step("Parse end timestamp"):
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify end is Sunday (weekday 6)"):
        assert end.weekday() == 6  # Sunday = 6 in Python's weekday()

    with allure.step("Verify week spans 7 days"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        duration = end - start
        assert duration.total_seconds() == 604800  # 7 days = 604800 seconds


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_week_timeframe_label_format(auth_client):
    """Week timeframe label matches YYYY-Wnn format"""
    with allure.step("Create week timeframe"):
        response = auth_client.get('/api/timeframes/week/2025-06-08')

    with allure.step("Verify label format matches pattern"):
        label = response['label']
        # Should be like "2025-W23" where W is literal and 23 is week number
        assert label.startswith('2025-W')
        week_part = label.split('-W')[1]
        assert week_part.isdigit()
        assert len(week_part) == 2


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_month_timeframe_starts_on_first_day(auth_client):
    """Month timeframe starts on day 1"""
    with allure.step("Create month timeframe for June 2025"):
        response = auth_client.get('/api/timeframes/month/2025-06-15')

    with allure.step("Parse start timestamp"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))

    with allure.step("Verify start is first day of month"):
        assert start.day == 1
        assert start.month == 6
        assert start.year == 2025


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_month_timeframe_ends_on_first_of_next_month(auth_client):
    """Month timeframe ends on first day of next month"""
    with allure.step("Create month timeframe for June 2025"):
        response = auth_client.get('/api/timeframes/month/2025-06-15')

    with allure.step("Parse end timestamp"):
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify end is first day of next month"):
        assert end.day == 1
        assert end.month == 7
        assert end.year == 2025


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_month_timeframe_label_format(auth_client):
    """Month timeframe label format"""
    with allure.step("Create month timeframe for June 2025"):
        response = auth_client.get('/api/timeframes/month/2025-06-15')

    with allure.step("Verify label format is 'Month Year'"):
        label = response['label']
        assert label == "June 2025"


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_season_winter_spans_dec_jan_feb(auth_client):
    """Season Winter spans Dec-Jan-Feb"""
    with allure.step("Create winter timeframe (December date)"):
        response = auth_client.get('/api/timeframes/season/2025-12-15')

    with allure.step("Parse timestamps"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify winter starts December 1"):
        assert start.month == 12
        assert start.day == 1
        assert start.year == 2025

    with allure.step("Verify winter ends March 1 (next year)"):
        assert end.month == 3
        assert end.day == 1
        assert end.year == 2026


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_season_spring_spans_mar_apr_may(auth_client):
    """Season Spring spans Mar-Apr-May"""
    with allure.step("Create spring timeframe"):
        response = auth_client.get('/api/timeframes/season/2025-04-15')

    with allure.step("Parse timestamps"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify spring starts March 1"):
        assert start.month == 3
        assert start.day == 1

    with allure.step("Verify spring ends June 1"):
        assert end.month == 6
        assert end.day == 1


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_season_summer_spans_jun_jul_aug(auth_client):
    """Season Summer spans Jun-Jul-Aug"""
    with allure.step("Create summer timeframe"):
        response = auth_client.get('/api/timeframes/season/2025-07-15')

    with allure.step("Parse timestamps"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify summer starts June 1"):
        assert start.month == 6
        assert start.day == 1

    with allure.step("Verify summer ends September 1"):
        assert end.month == 9
        assert end.day == 1


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_season_autumn_spans_sep_oct_nov(auth_client):
    """Season Autumn spans Sep-Oct-Nov"""
    with allure.step("Create autumn timeframe"):
        response = auth_client.get('/api/timeframes/season/2025-10-15')

    with allure.step("Parse timestamps"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify autumn starts September 1"):
        assert start.month == 9
        assert start.day == 1

    with allure.step("Verify autumn ends December 1"):
        assert end.month == 12
        assert end.day == 1


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_season_label_format(auth_client):
    """Season label format"""
    with allure.step("Create season timeframe"):
        response = auth_client.get('/api/timeframes/season/2025-07-15')

    with allure.step("Verify label exists and contains season and year"):
        label = response['label']
        assert label
        assert isinstance(label, str)
        # Label should be like "Summer 2025"
        assert '2025' in label
        assert 'Summer' in label


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_winter_crosses_year_boundary(auth_client):
    """Winter crosses year boundary (Dec 2025 includes Jan-Feb 2026)"""
    with allure.step("Create winter 2025 timeframe"):
        response = auth_client.get('/api/timeframes/season/2025-12-25')

    with allure.step("Parse timestamps"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify winter starts in December 2025"):
        assert start.month == 12
        assert start.year == 2025

    with allure.step("Verify winter ends in March 2026 (crosses year)"):
        assert end.month == 3
        assert end.year == 2026

    with allure.step("Verify label identifies winter by December year"):
        label = response['label']
        assert '2025' in label


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_year_timeframe_spans_jan_1_to_jan_1(auth_client):
    """Year timeframe spans Jan 1 to Jan 1 of next year"""
    with allure.step("Create year timeframe for 2025"):
        response = auth_client.get('/api/timeframes/year/2025-06-15')

    with allure.step("Parse timestamps"):
        start = datetime.fromisoformat(response['start_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(response['end_at'].replace('Z', '+00:00'))

    with allure.step("Verify year starts January 1, 2025"):
        assert start.month == 1
        assert start.day == 1
        assert start.year == 2025

    with allure.step("Verify year ends January 1, 2026"):
        assert end.month == 1
        assert end.day == 1
        assert end.year == 2026


@allure.feature('Timeframes')
@allure.story('Timeframe Boundaries')
@pytest.mark.timeframes
@allure.severity(allure.severity_level.NORMAL)
def test_year_timeframe_label_format(auth_client):
    """Year timeframe label is the year number"""
    with allure.step("Create year timeframe for 2025"):
        response = auth_client.get('/api/timeframes/year/2025-06-15')

    with allure.step("Verify label is year"):
        assert response['label'] == '2025'