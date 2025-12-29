from datetime import date, timedelta
from typing import Dict, Tuple, Optional
from ..dates.services import DateService
from .repositories import ReportRepository
from .models import DayReport, WeekReport, MonthReport, SeasonReport, YearReport
from src.utils.date_utils import get_week_sunday


class ReportService:
    def __init__(self, repository: ReportRepository):
        self.repository = repository
        self.date_service = DateService()

    def create_day_report(self, user_id: int, report_date: date, data: Dict) -> DayReport:
        return self.repository.create(
            DayReport,
            user_id=user_id,
            date=report_date,
            **data
        )

    def create_week_report(self, user_id: int, data: Dict) -> WeekReport:
        return self.repository.create(
            WeekReport,
            user_id=user_id,
            **data
        )

    def get_week_report(self, user_id: int, **filters) -> Optional[WeekReport]:
        """Get a week report with flexible filtering"""
        if 'date' in filters:
            # Convert date to week_sunday if date is provided
            filters['week_sunday'] = get_week_sunday(filters.pop('date'))
        return self.repository.get(WeekReport, user_id=user_id, **filters)

    def get_or_create_week_report(self, user_id: int, week_sunday: date) -> WeekReport:
        """Get existing week report or create a new empty one"""
        report = self.get_week_report(user_id, week_sunday=week_sunday)
        if not report:
            report = self.create_week_report(user_id, {'week_sunday': week_sunday})
        return report

    def create_month_report(self, user_id: int, month_date: date, data: Dict) -> MonthReport:
        return self.repository.create(
            MonthReport,
            user_id=user_id,
            month_date=month_date,
            **data
        )

    def create_season_report(self, user_id: int, start_date: date, end_date: date, data: Dict) -> SeasonReport:
        return self.repository.create(
            SeasonReport,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            **data
        )

    def create_year_report(self, user_id: int, year: int, data: Dict) -> YearReport:
        return self.repository.create(
            YearReport,
            user_id=user_id,
            year=year,
            **data
        )

    def get_or_create_day_report(self, user_id: int, report_date: date) -> DayReport:
        """Get existing day report or create a new empty one"""
        report = self.get_day_report(user_id, date=report_date)
        if not report:
            report = self.create_day_report(user_id, report_date, {})
        return report

    def get_day_report(self, user_id: int, **filters) -> Optional[DayReport]:
        """Get a day report with flexible filtering"""
        return self.repository.get(DayReport, user_id=user_id, **filters)


    def get_month_report(self, user_id: int, **filters) -> Optional[MonthReport]:
        """Get a month report with flexible filtering"""
        if 'date' in filters:
            # Convert date to month_date if date is provided
            filters['month_date'] = filters.pop('date').replace(day=1)
        return self.repository.get(MonthReport, user_id=user_id, **filters)

    def get_season_report(self, user_id: int, **filters) -> Optional[SeasonReport]:
        """Get a season report with flexible filtering"""
        if 'date' in filters:
            # Convert date to start_date and end_date if date is provided
            start_date, end_date = self.calculate_season_dates(filters.pop('date'))
            filters['start_date'] = start_date
            filters['end_date'] = end_date
        return self.repository.get(SeasonReport, user_id=user_id, **filters)

    def get_year_report(self, user_id: int, **filters) -> Optional[YearReport]:
        """Get a year report with flexible filtering"""
        if 'date' in filters:
            # Convert date to year if date is provided
            filters['year'] = filters.pop('date').year
        return self.repository.get(YearReport, user_id=user_id, **filters)


    def _get_report(self, report_type, **filters):
        """Internal generic get method, prefer specific get methods instead"""
        return self.repository.get(report_type, **filters)


    def list_reports(self, report_type, **filters):
        return self.repository.list(report_type, **filters)

    def update_report(self, report, data: Dict):
        return self.repository.update(report, **data)

    def delete_report(self, report):
        return self.repository.delete(report)

    @staticmethod
    def calculate_season_dates(year: int, season: str) -> Tuple[date, date]:
        """Calculate start and end dates for a given year and season"""
        season_dates = {
            'spring': (3, 5),
            'summer': (6, 8),
            'fall': (9, 11),
            'winter': (12, 2)
        }

        start_month, end_month = season_dates[season.lower()]

        # Handle winter season spanning year boundary
        if season.lower() == 'winter':
            start_date = date(year, start_month, 1)
            end_date = date(year + 1, end_month + 1, 1)
        else:
            start_date = date(year, start_month, 1)
            end_date = date(year, end_month + 1, 1)

        end_date = end_date - timedelta(days=1)

        return start_date, end_date