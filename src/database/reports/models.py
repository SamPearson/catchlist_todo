from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, validates
from src.database.db import db

from src.database.base.models import UserOwnedModel
from sqlalchemy import Column, Integer, Float, String, Text, Date


class BaseReport(UserOwnedModel):
    """Abstract base class for all reports"""
    __abstract__ = True

    notes = Column(Text)
    gratitudes = Column(Text)

    def as_dict(self):
        """Base dictionary representation"""
        data = super().as_dict()
        data.update({
            'notes': self.notes,
            'gratitudes': self.gratitudes
        })
        return data


class DayReport(BaseReport):
    """Daily report with ratings and notes"""

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

    week_sunday = Column(Date, nullable=False, index=True)
    weekly_goals = Column(Text)
    goals_rationale = Column(Text)
    start_notes = Column(Text)
    end_notes = Column(Text)
    goals_achieved_rating = Column(Integer)
    course_corrections = Column(Text)

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'week_sunday': self.week_sunday.isoformat() if self.week_sunday else None,
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

    month_date = Column(Date, nullable=False, index=True)
    monthly_goals = Column(Text)
    goals_rationale = Column(Text)
    start_notes = Column(Text)
    end_notes = Column(Text)
    goals_achieved_rating = Column(Integer)
    course_corrections = Column(Text)

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

    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    seasonal_theme = Column(Text)
    season_goals = Column(Text)
    goals_rationale = Column(Text)
    preseason_notes = Column(Text)
    postseason_notes = Column(Text)
    goals_achieved_rating = Column(Integer)
    course_corrections = Column(Text)

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

    year = Column(Integer, nullable=False, index=True)
    reflections = Column(Text)

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'year': self.year,
            'reflections': self.reflections
        })
        return data