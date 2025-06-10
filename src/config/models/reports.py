from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union
from sqlalchemy.orm import validates, Session as SQLAlchemySession
from sqlalchemy import func, Column, Integer, Float, Text, Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.ext.declarative import declared_attr
from .time_blocks import TimeBlock, DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from .checkin import Checkin
from ..db_setup import db

class BaseReport(db.Model):
    """Abstract base class for all report database models"""
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey('user.id'), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    notes = Column(Text)
    gratitudes = Column(Text)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stats = None
        self._commitments = None
        # Ensure each model has a time_block reference
        self.time_block = None

    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        # This will be overridden by subclasses
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "notes": self.notes,
            "gratitudes": self.gratitudes
        }

    @validates('prayer_rating', 'drugs_rating', 'distractions_rating', 'work_adherence', 
              'work_rpe', 'gains_rating', 'diet_adherence', 'cleaning_adherence', 
              'goals_achieved_rating')
    def validate_rating(self, key, value):
        if value is not None:  # Allow null values
            if not isinstance(value, int) or not (1 <= value <= 10):
                raise ValueError(f"{key} must be an integer between 1 and 10")
        return value
    
    # The commitments property has been removed as it's better to access
    # commitments directly through the time_block's commitments property
    # Time blocks already have the capability to retrieve commitments
    
    @property
    def stats(self) -> Dict:
        """Calculate basic statistics for the report"""
        if self._stats is None:
            # Get commitments directly from the time_block
            if hasattr(self, 'time_block') and self.time_block:
                commitments = self.time_block.commitments
                total = len(commitments)
                completed = sum(1 for c in commitments if c.completed)
                completion_rate = (completed / total * 100) if total > 0 else 0

                # Calculate average RPE from checkins
                rpe_values = []
                for commitment in commitments:
                    if commitment.checkins:
                        # Get the latest checkin with RPE
                        latest_checkin = max(commitment.checkins, key=lambda x: x.timestamp)
                        if latest_checkin.rpe is not None:
                            rpe_values.append(latest_checkin.rpe)

                avg_rpe = sum(rpe_values) / len(rpe_values) if rpe_values else None

                self._stats = {
                    "total_commitments": total,
                    "completed_commitments": completed,
                    "completion_rate": completion_rate,
                    "average_rpe": avg_rpe
                }
            else:
                self._stats = {
                    "total_commitments": 0,
                    "completed_commitments": 0,
                    "completion_rate": 0,
                    "average_rpe": None
                }
        return self._stats
    
    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        base_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "notes": self.notes,
            "gratitudes": self.gratitudes,
            "time_block": self.time_block.as_dict() if hasattr(self, 'time_block') else None,
            "stats": self.stats
        }
        return base_dict


class DayReport(BaseReport):
    """Database model for day reports"""
    __tablename__ = 'day_reports'

    date = Column(db.Date, nullable=False, index=True)
    sleep_hours = Column(Float)

    # 1-10 Scale Ratings
    prayer_rating = Column(Integer)
    drugs_rating = Column(Integer)
    distractions_rating = Column(Integer)
    work_adherence = Column(Integer)
    work_rpe = Column(Integer)
    gains_rating = Column(Integer)
    diet_adherence = Column(Integer)
    cleaning_adherence = Column(Integer)

    # Text blocks
    gains_text = Column(Text)

    # Relationship to day block
    day_block_id = Column(Integer, ForeignKey('day_block.id'))
    day_block = db.relationship('DayBlock', backref=db.backref('day_report', uselist=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_block = self.day_block

    # Add index for user_id and date together
    __table_args__ = (
        db.Index('idx_day_reports_user_date', 'user_id', 'date'),
    )

    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        data = super().as_dict()
        data.update({
            "date": self.date.isoformat() if self.date else None,
            "sleep_hours": self.sleep_hours,
            "prayer_rating": self.prayer_rating,
            "drugs_rating": self.drugs_rating,
            "distractions_rating": self.distractions_rating,
            "work_adherence": self.work_adherence,
            "work_rpe": self.work_rpe,
            "gains_rating": self.gains_rating,
            "diet_adherence": self.diet_adherence,
            "cleaning_adherence": self.cleaning_adherence,
            "gains_text": self.gains_text,
            "day_block_id": self.day_block_id
        })
        return data


class WeekReport(BaseReport):
    """Database model for week reports"""
    __tablename__ = 'week_reports'

    start_date = Column(db.Date, nullable=False, index=True)
    end_date = Column(db.Date, nullable=False, index=True)

    # Weekly specific fields
    weekly_goals = Column(Text)
    goals_rationale = Column(Text)
    start_notes = Column(Text)
    end_notes = Column(Text)
    goals_achieved_rating = Column(Integer)  # 1-10
    course_corrections = Column(Text)

    # Relationship to week block
    week_block_id = Column(Integer, ForeignKey('week_block.id'))
    week_block = db.relationship('WeekBlock', backref=db.backref('week_report', uselist=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_block = self.week_block

    # Add index for user_id and date range
    __table_args__ = (
        db.Index('idx_week_reports_user_dates', 'user_id', 'start_date', 'end_date'),
    )

    @property
    def day_reports(self):
        """Get all day reports for this week"""
        return db.session.query(DayReport).filter(
            DayReport.user_id == self.user_id,
            DayReport.date >= self.start_date,
            DayReport.date <= self.end_date
        ).all()

    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        data = super().as_dict()
        data.update({
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "weekly_goals": self.weekly_goals,
            "goals_rationale": self.goals_rationale,
            "start_notes": self.start_notes,
            "end_notes": self.end_notes,
            "goals_achieved_rating": self.goals_achieved_rating,
            "course_corrections": self.course_corrections,
            "day_reports": [report.as_dict() for report in self.day_reports],
            "week_block_id": self.week_block_id
        })
        return data


class MonthReport(BaseReport):
    """Database model for month reports"""
    __tablename__ = 'month_reports'

    month = Column(db.Date, nullable=False, index=True)  # Store first day of month

    # Month specific fields
    monthly_goals = Column(Text)
    goals_rationale = Column(Text)
    start_notes = Column(Text)
    end_notes = Column(Text)
    goals_achieved_rating = Column(Integer)  # 1-10
    course_corrections = Column(Text)

    # Relationship to month block
    month_block_id = Column(Integer, ForeignKey('month_block.id'))
    month_block = db.relationship('MonthBlock', backref=db.backref('month_report', uselist=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_block = self.month_block

    # Add index for user_id and month
    __table_args__ = (
        db.Index('idx_month_reports_user_month', 'user_id', 'month'),
    )

    @property
    def week_reports(self):
        """Get all week reports for this month"""
        month_end = datetime(self.month.year, self.month.month + 1, 1) if self.month.month < 12 else datetime(self.month.year + 1, 1, 1)
        month_end = month_end - timedelta(days=1)

        return db.session.query(WeekReport).filter(
            WeekReport.user_id == self.user_id,
            WeekReport.start_date >= self.month,
            WeekReport.end_date <= month_end
        ).all()

    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        data = super().as_dict()
        data.update({
            "month": self.month.isoformat() if self.month else None,
            "monthly_goals": self.monthly_goals,
            "goals_rationale": self.goals_rationale,
            "start_notes": self.start_notes,
            "end_notes": self.end_notes,
            "goals_achieved_rating": self.goals_achieved_rating,
            "course_corrections": self.course_corrections,
            "week_reports": [report.as_dict() for report in self.week_reports],
            "month_block_id": self.month_block_id
        })
        return data


class SeasonReport(BaseReport):
    """Database model for season reports"""
    __tablename__ = 'season_reports'

    start_date = Column(db.Date, nullable=False, index=True)
    end_date = Column(db.Date, nullable=False, index=True)

    # Season specific fields
    seasonal_theme = Column(String(255))
    season_goals = Column(Text)
    goals_rationale = Column(Text)
    preseason_notes = Column(Text)
    postseason_notes = Column(Text)
    goals_achieved_rating = Column(Integer)  # 1-10
    course_corrections = Column(Text)

    # Relationship to season block
    season_block_id = Column(Integer, ForeignKey('season_block.id'))
    season_block = db.relationship('SeasonBlock', backref=db.backref('season_report', uselist=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_block = self.season_block

    # Add index for user_id and date range
    __table_args__ = (
        db.Index('idx_season_reports_user_dates', 'user_id', 'start_date', 'end_date'),
    )

    @property
    def month_reports(self):
        """Get all month reports for this season"""
        return db.session.query(MonthReport).filter(
            MonthReport.user_id == self.user_id,
            MonthReport.month >= self.start_date,
            func.date_add(MonthReport.month, text("interval 1 month")) <= self.end_date
        ).all()

    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        data = super().as_dict()
        data.update({
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "seasonal_theme": self.seasonal_theme,
            "season_goals": self.season_goals,
            "goals_rationale": self.goals_rationale,
            "preseason_notes": self.preseason_notes,
            "postseason_notes": self.postseason_notes,
            "goals_achieved_rating": self.goals_achieved_rating,
            "course_corrections": self.course_corrections,
            "month_reports": [report.as_dict() for report in self.month_reports],
            "season_block_id": self.season_block_id
        })
        return data


class YearReport(BaseReport):
    """Database model for year reports"""
    __tablename__ = 'year_reports'

    year = Column(Integer, nullable=False, index=True)
    reflections = Column(Text)

    # Relationship to year block
    year_block_id = Column(Integer, ForeignKey('year_block.id'))
    year_block = db.relationship('YearBlock', backref=db.backref('year_report', uselist=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_block = self.year_block

    # Add index for user_id and year
    __table_args__ = (
        db.Index('idx_year_reports_user_year', 'user_id', 'year'),
    )

    @property
    def season_reports(self):
        """Get all season reports for this year"""
        year_start = date(self.year, 1, 1)
        year_end = date(self.year, 12, 31)

        return db.session.query(SeasonReport).filter(
            SeasonReport.user_id == self.user_id,
            SeasonReport.start_date >= year_start,
            SeasonReport.end_date <= year_end
        ).all()

    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        data = super().as_dict()
        data.update({
            "year": self.year,
            "reflections": self.reflections,
            "season_reports": [report.as_dict() for report in self.season_reports],
            "year_block_id": self.year_block_id
        })
        return data


class ReportGenerator:
    @staticmethod
    def generate_missing_reports(user_id: int, db: SQLAlchemySession):
        """Generate any missing reports for the user"""
        today = date.today()
        
        # Check last 7 days
        for i in range(7):
            check_date = today - timedelta(days=i)
            day_block = DayBlock.get_or_create(db, user_id, check_date.year, check_date.month, check_date.day)
            
            # Create day report if missing
            if not db.query(DayReport).filter_by(
                user_id=user_id, date=check_date).first():
                ReportGenerator.create_day_report_model(user_id, check_date, db)

        # Check last 4 weeks
        for i in range(4):
            check_date = today - timedelta(weeks=i)
            week_number = check_date.isocalendar()[1]
            week_block = WeekBlock.get_or_create(db, user_id, check_date.year, week_number)

            # Create week report if missing
            if not db.query(WeekReport).filter_by(
                user_id=user_id, start_date=week_block.start_date, end_date=week_block.end_date).first():
                ReportGenerator.create_week_report_model(user_id, week_block, db)

        # Check last 3 months
        for i in range(3):
            month_date = date(today.year, today.month - i if today.month > i else 12 - (i - today.month), 1)
            month_block = MonthBlock.get_or_create(db, user_id, month_date.year, month_date.month)

            # Create month report if missing
            if not db.query(MonthReport).filter_by(
                user_id=user_id, month=month_block.start_date).first():
                ReportGenerator.create_month_report_model(user_id, month_block, db)
    
    @staticmethod
    def calculate_metrics_from_checkins(user_id: int, start_date: date, end_date: date, db: SQLAlchemySession) -> Dict:
        """Calculate metrics from checkins in a date range"""
        # Get all checkins for the time period
        checkins = db.query(Checkin).filter(
            Checkin.user_id == user_id,
            func.date(Checkin.timestamp) >= start_date,
            func.date(Checkin.timestamp) <= end_date
        ).all()

        # Calculate metrics
        rpe_values = [c.rpe for c in checkins if c.rpe is not None]
        mood_values = [c.mood for c in checkins if c.mood is not None]
        energy_values = [c.energy for c in checkins if c.energy is not None]

        return {
            "rpe": sum(rpe_values) / len(rpe_values) if rpe_values else None,
            "mood": sum(mood_values) / len(mood_values) if mood_values else None,
            "energy": sum(energy_values) / len(energy_values) if energy_values else None,
            "checkin_count": len(checkins)
        }

    @staticmethod
    def create_day_report_model(user_id: int, report_date: date, db: SQLAlchemySession):
        """Create a day report model for the given date"""
        # Find the day block for this date
        day_block = db.query(DayBlock).filter_by(
            user_id=user_id,
            start_date=report_date
        ).first()

        if not day_block:
            # Create day block if it doesn't exist
            day_block = DayBlock.get_or_create(
                db, user_id, report_date.year, report_date.month, report_date.day)

        # Calculate metrics from checkins
        metrics = ReportGenerator.calculate_metrics_from_checkins(
            user_id, report_date, report_date, db)

        # Update day block with metrics
        day_block.rpe = metrics["rpe"]
        day_block.mood = metrics["mood"]
        day_block.energy = metrics["energy"]
        day_block.report_generated = True

        # Create the report model
        day_report = DayReport(
            user_id=user_id,
            date=report_date,
            day_block_id=day_block.id,
            # Default values can be set here
        )

        db.add(day_report)
        db.commit()
        return day_report

    @staticmethod
    def create_week_report_model(user_id: int, week_block: WeekBlock, db: SQLAlchemySession):
        """Create a week report model for the given week block"""
        # Calculate metrics from checkins for the week
        metrics = ReportGenerator.calculate_metrics_from_checkins(
            user_id, week_block.start_date, week_block.end_date, db)

        # Update week block with metrics
        week_block.rpe = metrics["rpe"]
        week_block.mood = metrics["mood"]
        week_block.report_generated = True

        # Create the report model
        week_report = WeekReport(
            user_id=user_id,
            start_date=week_block.start_date,
            end_date=week_block.end_date,
            week_block_id=week_block.id,
            # Default values can be set here
        )

        db.add(week_report)
        db.commit()
        return week_report

    @staticmethod
    def create_month_report_model(user_id: int, month_block: MonthBlock, db: SQLAlchemySession):
        """Create a month report model for the given month block"""
        # Create the report model
        month_report = MonthReport(
            user_id=user_id,
            month=month_block.start_date,
            month_block_id=month_block.id,
            # Default values can be set here
        )

        db.add(month_report)
        db.commit()
        return month_report

    @staticmethod
    def create_season_report_model(user_id: int, season_block: SeasonBlock, db: SQLAlchemySession):
        """Create a season report model for the given season block"""
        # Create the report model
        season_report = SeasonReport(
            user_id=user_id,
            start_date=season_block.start_date,
            end_date=season_block.end_date,
            season_block_id=season_block.id,
            seasonal_theme=season_block.season_theme,
            # Default values can be set here
        )

        db.add(season_report)
        db.commit()
        return season_report

    @staticmethod
    def create_year_report_model(user_id: int, year_block: YearBlock, db: SQLAlchemySession):
        """Create a year report model for the given year block"""
        # Create the report model
        year_report = YearReport(
            user_id=user_id,
            year=year_block.year,
            year_block_id=year_block.id,
            # Default values can be set here
        )

        db.add(year_report)
        db.commit()
        return year_report