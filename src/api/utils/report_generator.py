from datetime import datetime, timedelta
from ...config.models import db, Checkin, DayReport, WeekReport, MonthReport, SeasonReport, YearReport
from ...config.models import WeekBlock, MonthBlock, SeasonBlock, YearBlock
from ...config.models.reports import ReportGenerator as ModelReportGenerator

class ReportGenerator:
    @staticmethod
    def generate_missing_reports(user_id, session):
        """Generate any missing reports for the user"""
        # Use the ReportGenerator from models to generate reports
        ModelReportGenerator.generate_missing_reports(user_id, session)

    @staticmethod
    def get_report(user_id, date, report_type, session):
        """Get a report for the specified date and type

        Args:
            user_id: The user ID
            date: The date for the report
            report_type: One of 'day', 'week', 'month', 'season', 'year'
            session: Database session
        """
        model_map = {
            'day': (DayReport, None),
            'week': (WeekReport, WeekBlock),
            'month': (MonthReport, MonthBlock),
            'season': (SeasonReport, SeasonBlock),
            'year': (YearReport, YearBlock)
        }

        ReportModel, BlockModel = model_map.get(report_type, (None, None))

        if not ReportModel:
            raise ValueError(f"Invalid report type: {report_type}")

        if report_type == 'day':
            # Day reports don't use a time block for filtering
            report = session.query(ReportModel).filter_by(
                user_id=user_id,
                date=date
            ).first()

            if not report:
                report = ModelReportGenerator.create_day_report_model(user_id, date, session)
        else:
            # All other report types need a time block
            if report_type == 'week':
                year, week_num, _ = date.isocalendar()
                time_block = BlockModel.get_or_create(session, user_id, year, week_num)
                creator_method = ModelReportGenerator.create_week_report_model
            elif report_type == 'month':
                time_block = BlockModel.get_or_create(session, user_id, date.year, date.month)
                creator_method = ModelReportGenerator.create_month_report_model
            elif report_type == 'season':
                # Determine season from date
                month = date.month
                if 3 <= month <= 5:
                    season = 'spring'
                elif 6 <= month <= 8:
                    season = 'summer'
                elif 9 <= month <= 11:
                    season = 'fall'
                else:
                    season = 'winter'
                time_block = BlockModel.get_or_create(session, user_id, date.year, season)
                creator_method = ModelReportGenerator.create_season_report_model
            else:  # year
                time_block = BlockModel.get_or_create(session, user_id, date.year)
                creator_method = ModelReportGenerator.create_year_report_model

            # Look for an existing report
            report = session.query(ReportModel).filter_by(
                user_id=user_id,
                start_date=time_block.start_date,
                end_date=time_block.end_date
            ).first()

            # If no report exists, create one
            if not report:
                report = creator_method(user_id, time_block, session)

        return report.as_dict() if report else None

    @staticmethod
    def get_day_report(user_id, date, session):
        """Get a day report for the specified date"""
        return ReportGenerator.get_report(user_id, date, 'day', session)

    @staticmethod
    def get_week_report(user_id, date, session):
        """Get a week report containing the specified date"""
        return ReportGenerator.get_report(user_id, date, 'week', session)

    @staticmethod
    def get_month_report(user_id, date, session):
        """Get a month report containing the specified date"""
        return ReportGenerator.get_report(user_id, date, 'month', session)

    @staticmethod
    def get_season_report(user_id, date, session):
        """Get a season report containing the specified date"""
        return ReportGenerator.get_report(user_id, date, 'season', session)

    @staticmethod
    def get_year_report(user_id, date, session):
        """Get a year report containing the specified date"""
        return ReportGenerator.get_report(user_id, date, 'year', session)