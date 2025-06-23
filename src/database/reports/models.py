from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, validates
from ...config.db_setup import db

class BaseReport(db.Model):
    """Abstract base class for all reports"""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    notes = Column(Text)
    gratitudes = Column(Text)

    @validates('*_rating', '*_adherence', '*_rpe')
    def validate_rating(self, key, value):
        if value is not None and not (1 <= value <= 10):
            raise ValueError(f"{key} must be between 1 and 10")
        return value

    def as_dict(self):
        """Base dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes,
            'gratitudes': self.gratitudes
        }

class DayReport(BaseReport):
    """Daily report with ratings and notes"""
    __tablename__ = 'day_reports'

    date = Column(Date, nullable=False, index=True)
    sleep_hours = Column(Integer)
    prayer_rating = Column(Integer)
    drugs_rating = Column(Integer)
    distractions_rating = Column(Integer)
    work_adherence = Column(Integer)
    work_rpe = Column(Integer)
    gains_rating = Column(Integer)
    diet_adherence = Column(Integer)
    cleaning_adherence = Column(Integer)
    gains = Column(Text)

    __table_args__ = (db.Index('idx_day_user_date', 'user_id', 'date'),)

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'date': self.date.isoformat() if self.date else None,
            'sleep_hours': self.sleep_hours,
            'prayer_rating': self.prayer_rating,
            'drugs_rating': self.drugs_rating,
            'distractions_rating': self.distractions_rating,
            'work_adherence': self.work_adherence,
            'work_rpe': self.work_rpe,
            'gains_rating': self.gains_rating,
            'diet_adherence': self.diet_adherence,
            'cleaning_adherence': self.cleaning_adherence,
            'gains': self.gains
        })
        return data

class WeekReport(BaseReport):
    """Weekly planning and review"""
    __tablename__ = 'week_reports'

    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    weekly_goals = Column(Text)
    goals_rationale = Column(Text)
    start_notes = Column(Text)
    end_notes = Column(Text)
    goals_achieved_rating = Column(Integer)
    course_corrections = Column(Text)

    __table_args__ = (db.Index('idx_week_user_date', 'user_id', 'start_date'),)

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'weekly_goals': self.weekly_goals,
            'goals_rationale': self.goals_rationale,
            'start_notes': self.start_notes,
            'end_notes': self.end_notes,
            'goals_achieved_rating': self.goals_achieved_rating,
            'course_corrections': self.course_corrections
        })
        return data

class MonthReport(BaseReport):
    """Monthly planning and review"""
    __tablename__ = 'month_reports'

    month_date = Column(Date, nullable=False, index=True)
    monthly_goals = Column(Text)
    goals_rationale = Column(Text)
    start_notes = Column(Text)
    end_notes = Column(Text)
    goals_achieved_rating = Column(Integer)
    course_corrections = Column(Text)

    __table_args__ = (db.Index('idx_month_user_date', 'user_id', 'month_date'),)

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'month_date': self.month_date.isoformat() if self.month_date else None,
            'monthly_goals': self.monthly_goals,
            'goals_rationale': self.goals_rationale,
            'start_notes': self.start_notes,
            'end_notes': self.end_notes,
            'goals_achieved_rating': self.goals_achieved_rating,
            'course_corrections': self.course_corrections
        })
        return data

class SeasonReport(BaseReport):
    """Seasonal planning and review"""
    __tablename__ = 'season_reports'

    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    seasonal_theme = Column(Text)
    season_goals = Column(Text)
    goals_rationale = Column(Text)
    preseason_notes = Column(Text)
    postseason_notes = Column(Text)
    goals_achieved_rating = Column(Integer)
    course_corrections = Column(Text)

    __table_args__ = (db.Index('idx_season_user_date', 'user_id', 'start_date'),)

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'seasonal_theme': self.seasonal_theme,
            'season_goals': self.season_goals,
            'goals_rationale': self.goals_rationale,
            'preseason_notes': self.preseason_notes,
            'postseason_notes': self.postseason_notes,
            'goals_achieved_rating': self.goals_achieved_rating,
            'course_corrections': self.course_corrections
        })
        return data

class YearReport(BaseReport):
    """Yearly reflection"""
    __tablename__ = 'year_reports'

    year = Column(Integer, nullable=False, index=True)
    reflections = Column(Text)

    __table_args__ = (db.Index('idx_year_user', 'user_id', 'year'),)

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'year': self.year,
            'reflections': self.reflections
        })
        return data