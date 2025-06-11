from flask import jsonify, request, current_app
from datetime import datetime, date
from flask_jwt_extended import get_jwt_identity
from ...utils.helpers import get_current_user_id
from ....config.models import db
from ...utils.report_generator import ReportGenerator
from ....config.models.reports import ReportGenerator as ModelReportGenerator

class BaseReportEndpoint:
    """Base class for report endpoints with common functionality"""
    def __init__(self, report_type, report_model, block_model, date_format='%Y-%m-%d'):
        self.report_type = report_type
        self.report_model = report_model
        self.block_model = block_model
        self.date_format = date_format

    def get_report(self, date_str):
        """Get a report for the specified date"""
        user_id = get_current_user_id()

        try:
            report_date = datetime.strptime(date_str, self.date_format).date()

            # Use the correct report type method
            if self.report_type == 'day':
                report_data = ReportGenerator.get_day_report(user_id, report_date, db.session)
            elif self.report_type == 'week':
                report_data = ReportGenerator.get_week_report(user_id, report_date, db.session)
            elif self.report_type == 'month':
                report_data = ReportGenerator.get_month_report(user_id, report_date, db.session)
            elif self.report_type == 'season':
                report_data = ReportGenerator.get_season_report(user_id, report_date, db.session)
            elif self.report_type == 'year':
                report_data = ReportGenerator.get_year_report(user_id, report_date, db.session)
            else:
                return jsonify({"error": f"Invalid report type: {self.report_type}"}), 400

            if not report_data:
                return jsonify({"error": f"Failed to generate {self.report_type} report"}), 500

            return jsonify(report_data)
        except ValueError as e:
            return jsonify({"error": f"Invalid date format. Use {self.date_format}"}), 400
        except Exception as e:
            current_app.logger.error(f"Error generating {self.report_type} report: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def create_report(self):
        """Create a new report"""
        user_id = get_current_user_id()
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            # Different handling based on report type
            if self.report_type == 'day':
                date_str = data.get('date')
                if not date_str:
                    return jsonify({"error": "Date is required"}), 400

                report_date = datetime.strptime(date_str, self.date_format).date()

                # Check if report already exists
                existing_report = self.report_model.query.filter_by(
                    user_id=user_id,
                    date=report_date
                ).first()

                if existing_report:
                    return jsonify({"error": "Report already exists for this date"}), 409

                # Create the report
                report = ModelReportGenerator.create_day_report_model(user_id, report_date, db.session)

            elif self.report_type == 'year':
                year = data.get('year')
                if not year:
                    return jsonify({"error": "Year is required"}), 400

                # Check if report already exists
                existing_report = self.report_model.query.filter_by(
                    user_id=user_id,
                    year=year
                ).first()

                if existing_report:
                    return jsonify({"error": "Report already exists for this year"}), 409

                # Get or create year block
                year_block = self.block_model.get_or_create(db.session, user_id, year)
                report = ModelReportGenerator.create_year_report_model(user_id, year_block, db.session)
            else:
                # Week, Month, Season all use a date to identify the period
                date_str = data.get('date')
                if not date_str:
                    return jsonify({"error": "Date is required"}), 400

                report_date = datetime.strptime(date_str, self.date_format).date()

                # Get the appropriate block
                if self.report_type == 'week':
                    year, week_num, _ = report_date.isocalendar()
                    time_block = self.block_model.get_or_create(db.session, user_id, year, week_num)
                    creator_method = ModelReportGenerator.create_week_report_model
                elif self.report_type == 'month':
                    time_block = self.block_model.get_or_create(db.session, user_id, report_date.year, report_date.month)
                    creator_method = ModelReportGenerator.create_month_report_model
                elif self.report_type == 'season':
                    # Determine season from date
                    month = report_date.month
                    if 3 <= month <= 5:
                        season = 'spring'
                    elif 6 <= month <= 8:
                        season = 'summer'
                    elif 9 <= month <= 11:
                        season = 'fall'
                    else:
                        season = 'winter'
                    time_block = self.block_model.get_or_create(db.session, user_id, report_date.year, season)
                    creator_method = ModelReportGenerator.create_season_report_model

                # Check if report already exists
                if self.report_type == 'month':
                    existing_report = self.report_model.query.filter_by(
                        user_id=user_id,
                        month=time_block.start_date
                    ).first()
                else:
                    existing_report = self.report_model.query.filter_by(
                        user_id=user_id,
                        start_date=time_block.start_date,
                        end_date=time_block.end_date
                    ).first()

                if existing_report:
                    return jsonify({"error": f"Report already exists for this {self.report_type}"}), 409

                # Create the report
                report = creator_method(user_id, time_block, db.session)


            return jsonify(report.as_dict()), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error creating {self.report_type} report: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def update_report(self, report_id):
        """Update an existing report"""
        user_id = get_current_user_id()
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            # Find the report
            report = self.report_model.query.filter_by(id=report_id, user_id=user_id).first()

            if not report:
                return jsonify({"error": "Report not found"}), 404

            # Update fields based on report type
            common_fields = ['notes', 'gratitudes']
            for field in common_fields:
                if field in data:
                    setattr(report, field, data[field])

            # Type-specific fields
            if self.report_type == 'day':
                day_fields = [
                    'sleep_hours', 'prayer_rating', 'drugs_rating', 
                    'distractions_rating', 'work_adherence', 'work_rpe',
                    'gains_rating', 'diet_adherence', 'cleaning_adherence',
                    'gains_text'
                ]
                for field in day_fields:
                    if field in data:
                        setattr(report, field, data[field])
            elif self.report_type == 'week':
                week_fields = [
                    'weekly_goals', 'goals_rationale', 'start_notes',
                    'end_notes', 'goals_achieved_rating', 'course_corrections'
                ]
                for field in week_fields:
                    if field in data:
                        setattr(report, field, data[field])
            elif self.report_type == 'month':
                month_fields = [
                    'monthly_goals', 'goals_rationale', 'start_notes',
                    'end_notes', 'goals_achieved_rating', 'course_corrections'
                ]
                for field in month_fields:
                    if field in data:
                        setattr(report, field, data[field])
            elif self.report_type == 'season':
                season_fields = [
                    'seasonal_theme', 'season_goals', 'goals_rationale',
                    'preseason_notes', 'postseason_notes', 'goals_achieved_rating',
                    'course_corrections'
                ]
                for field in season_fields:
                    if field in data:
                        setattr(report, field, data[field])
            elif self.report_type == 'year':
                year_fields = ['reflections']
                for field in year_fields:
                    if field in data:
                        setattr(report, field, data[field])

            # Save changes
            db.session.commit()

            return jsonify(report.as_dict())
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating {self.report_type} report: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def delete_report(self, report_id):
        """Delete a report"""
        user_id = get_current_user_id()

        try:
            # Find the report
            report = self.report_model.query.filter_by(id=report_id, user_id=user_id).first()

            if not report:
                return jsonify({"error": "Report not found"}), 404

            # Delete the report
            db.session.delete(report)
            db.session.commit()

            return jsonify({"message": f"{self.report_type.capitalize()} report deleted successfully"})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting {self.report_type} report: {str(e)}")
            return jsonify({"error": str(e)}), 500
