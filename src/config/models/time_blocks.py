from datetime import datetime, date, timedelta
from ..db_setup import db
from sqlalchemy.orm import foreign
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, List
from .commitment import Commitment
from sqlalchemy.orm import Session as DBSession

class TimeBlock(db.Model):
    """Base class for all time blocks"""
    
    __tablename__ = 'time_block'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    block_type = db.Column(db.String(50), nullable=False)
    theme = db.Column(db.String(255))  # Theme for the time block
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship('User', backref='time_blocks')
    checkins = relationship('Checkin', 
                          primaryjoin="TimeBlock.id==Checkin.time_block_id",
                          back_populates="time_block",
                          lazy='dynamic')
    
    __mapper_args__ = {
        'polymorphic_identity': 'time_block',
        'polymorphic_on': block_type
    }
    
    def __init__(self, user_id: int, block_type: str, theme: str = None):
        self.user_id = user_id
        self.block_type = block_type
        if theme:
            self.theme = theme
    
    def as_dict(self) -> Dict:
        """Convert the time block to a dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'block_type': self.block_type,
            'theme': self.theme,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def commitments(self) -> List[Commitment]:
        """Get all commitments for this time block"""
        return Commitment.query.filter(
            Commitment.user_id == self.user_id,
            Commitment.due_date.between(self.start_date, self.end_date)
        ).all()


class DayBlock(TimeBlock):
    """A time block representing a day"""
    
    __tablename__ = 'day_block'
    
    id = db.Column(db.Integer, db.ForeignKey('time_block.id'), primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    sleep_hours = db.Column(db.Float)
    mood = db.Column(db.Integer)  # Changed to Integer for 1-10 scale
    rpe = db.Column(db.Integer)  # Rating of perceived exertion (1-10)
    food_notes = db.Column(db.Text)
    gains = db.Column(db.Text)
    gratitudes = db.Column(db.Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'day'
    }
    
    def __init__(self, user_id: int, year: int, month: int, day: int, 
                 sleep_hours: float = None, mood: int = None, rpe: int = None,
                 food_notes: str = None, gains: str = None, gratitudes: str = None):
        start_date = date(year, month, day)
        end_date = start_date
        super().__init__(user_id=user_id, block_type='day')
        self.year = year
        self.month = month
        self.day = day
        self.start_date = start_date
        self.end_date = end_date
        if sleep_hours is not None:
            self.sleep_hours = sleep_hours
        if mood is not None:
            self.mood = mood
        if rpe is not None:
            self.rpe = rpe
        if food_notes:
            self.food_notes = food_notes
        if gains:
            self.gains = gains
        if gratitudes:
            self.gratitudes = gratitudes
    
    @classmethod
    def get_or_create(cls, db: DBSession, user_id: int, year: int, month: int, day: int) -> 'DayBlock':
        """Get an existing day block or create a new one"""
        day_block = db.query(cls).filter_by(
            user_id=user_id,
            year=year,
            month=month,
            day=day
        ).first()
        
        if not day_block:
            day_block = cls(user_id=user_id, year=year, month=month, day=day)
            db.add(day_block)
            db.commit()
        
        return day_block
    
    def linked_commitments(self, db: DBSession) -> List[Commitment]:
        """Get all commitments linked to this day block"""
        return Commitment.query.filter(
            Commitment.user_id == self.user_id,
            Commitment.due_date == self.start_date
        ).all()
    
    def as_dict(self) -> Dict:
        """Convert the day block to a dictionary"""
        data = super().as_dict()
        data.update({
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'sleep_hours': self.sleep_hours,
            'mood': self.mood,
            'rpe': self.rpe,
            'food_notes': self.food_notes,
            'gains': self.gains,
            'gratitudes': self.gratitudes
        })
        return data


class WeekBlock(TimeBlock):
    """A time block representing a week"""
    
    __tablename__ = 'week_block'
    
    id = db.Column(db.Integer, db.ForeignKey('time_block.id'), primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    weekly_aim = db.Column(db.String(255))
    weekly_notes = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Weekly RPE (1-10)
    gains = db.Column(db.Text)
    gratitudes = db.Column(db.Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'week'
    }
    
    def __init__(self, user_id: int, year: int, week_number: int, 
                 weekly_aim: str = None, weekly_notes: str = None,
                 rpe: int = None, gains: str = None, gratitudes: str = None):
        # Calculate start and end dates for the week
        start_date = datetime.strptime(f'{year}-W{week_number:02d}-1', '%Y-W%W-%w').date()
        end_date = start_date + timedelta(days=6)
        
        super().__init__(user_id=user_id, block_type='week')
        self.year = year
        self.week_number = week_number
        self.start_date = start_date
        self.end_date = end_date
        if weekly_aim:
            self.weekly_aim = weekly_aim
        if weekly_notes:
            self.weekly_notes = weekly_notes
        if rpe is not None:
            self.rpe = rpe
        if gains:
            self.gains = gains
        if gratitudes:
            self.gratitudes = gratitudes
    
    @classmethod
    def get_or_create(cls, db: DBSession, user_id: int, year: int, week_number: int) -> 'WeekBlock':
        """Get an existing week block or create a new one"""
        week_block = db.query(cls).filter_by(
            user_id=user_id,
            year=year,
            week_number=week_number
        ).first()
        
        if not week_block:
            week_block = cls(user_id=user_id, year=year, week_number=week_number)
            db.add(week_block)
            db.commit()
        
        return week_block
    
    def as_dict(self) -> Dict:
        """Convert the week block to a dictionary"""
        data = super().as_dict()
        data.update({
            'year': self.year,
            'week_number': self.week_number,
            'weekly_aim': self.weekly_aim,
            'weekly_notes': self.weekly_notes,
            'rpe': self.rpe,
            'gains': self.gains,
            'gratitudes': self.gratitudes
        })
        return data


class MonthBlock(TimeBlock):
    """A time block representing a month"""
    
    __tablename__ = 'month_block'
    
    id = db.Column(db.Integer, db.ForeignKey('time_block.id'), primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    month_theme = db.Column(db.String(255))  # Renamed from theme to month_theme
    goals = db.Column(db.Text)
    goals_rationale = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Monthly RPE (1-10)
    gains = db.Column(db.Text)
    gratitudes = db.Column(db.Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'month'
    }
    
    def __init__(self, user_id: int, year: int, month: int, 
                 theme: str = None, goals: str = None, goals_rationale: str = None,
                 rpe: int = None, gains: str = None, gratitudes: str = None):
        # Calculate start and end dates for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        super().__init__(user_id=user_id, block_type='month', theme=theme)
        self.year = year
        self.month = month
        self.start_date = start_date
        self.end_date = end_date
        if theme:
            self.month_theme = theme
        if goals:
            self.goals = goals
        if goals_rationale:
            self.goals_rationale = goals_rationale
        if rpe is not None:
            self.rpe = rpe
        if gains:
            self.gains = gains
        if gratitudes:
            self.gratitudes = gratitudes
    
    @classmethod
    def get_or_create(cls, db: DBSession, user_id: int, year: int, month: int) -> 'MonthBlock':
        """Get an existing month block or create a new one"""
        month_block = db.query(cls).filter_by(
            user_id=user_id,
            year=year,
            month=month
        ).first()
        
        if not month_block:
            month_block = cls(user_id=user_id, year=year, month=month)
            db.add(month_block)
            db.commit()
        
        return month_block
    
    def as_dict(self) -> Dict:
        """Convert the month block to a dictionary"""
        data = super().as_dict()
        data.update({
            'year': self.year,
            'month': self.month,
            'month_theme': self.month_theme,
            'goals': self.goals,
            'goals_rationale': self.goals_rationale,
            'rpe': self.rpe,
            'gains': self.gains,
            'gratitudes': self.gratitudes
        })
        return data


class SeasonBlock(TimeBlock):
    """A time block representing a season"""
    
    __tablename__ = 'season_block'
    
    id = db.Column(db.Integer, db.ForeignKey('time_block.id'), primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    season = db.Column(db.String(20), nullable=False)  # spring, summer, fall, winter
    season_theme = db.Column(db.String(255))  # Renamed from theme to season_theme
    goals = db.Column(db.Text)
    goals_rationale = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Seasonal RPE (1-10)
    gains = db.Column(db.Text)
    gratitudes = db.Column(db.Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'season'
    }
    
    def __init__(self, user_id: int, year: int, season: str,
                 theme: str = None, goals: str = None, goals_rationale: str = None,
                 rpe: int = None, gains: str = None, gratitudes: str = None):
        # Calculate start and end dates for the season
        if season == 'spring':
            start_date = date(year, 3, 1)
            end_date = date(year, 5, 31)
        elif season == 'summer':
            start_date = date(year, 6, 1)
            end_date = date(year, 8, 31)
        elif season == 'fall':
            start_date = date(year, 9, 1)
            end_date = date(year, 11, 30)
        else:  # winter
            start_date = date(year, 12, 1)
            end_date = date(year + 1, 2, 28)
        
        super().__init__(user_id=user_id, block_type='season', theme=theme)
        self.year = year
        self.season = season
        self.start_date = start_date
        self.end_date = end_date
        if theme:
            self.season_theme = theme
        if goals:
            self.goals = goals
        if goals_rationale:
            self.goals_rationale = goals_rationale
        if rpe is not None:
            self.rpe = rpe
        if gains:
            self.gains = gains
        if gratitudes:
            self.gratitudes = gratitudes
    
    @classmethod
    def get_or_create(cls, db: DBSession, user_id: int, year: int, season: str) -> 'SeasonBlock':
        """Get an existing season block or create a new one"""
        season_block = db.query(cls).filter_by(
            user_id=user_id,
            year=year,
            season=season
        ).first()
        
        if not season_block:
            season_block = cls(user_id=user_id, year=year, season=season)
            db.add(season_block)
            db.commit()
        
        return season_block
    
    def as_dict(self) -> Dict:
        """Convert the season block to a dictionary"""
        data = super().as_dict()
        data.update({
            'year': self.year,
            'season': self.season,
            'season_theme': self.season_theme,
            'goals': self.goals,
            'goals_rationale': self.goals_rationale,
            'rpe': self.rpe,
            'gains': self.gains,
            'gratitudes': self.gratitudes
        })
        return data


class YearBlock(TimeBlock):
    """A time block representing a year"""
    
    __tablename__ = 'year_block'
    
    id = db.Column(db.Integer, db.ForeignKey('time_block.id'), primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    year_theme = db.Column(db.String(255))  # Renamed from theme to year_theme
    goals = db.Column(db.Text)
    goals_rationale = db.Column(db.Text)
    rpe = db.Column(db.Integer)  # Yearly RPE (1-10)
    gains = db.Column(db.Text)
    gratitudes = db.Column(db.Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'year'
    }
    
    def __init__(self, user_id: int, year: int, theme: str = None):
        # Calculate start and end dates for the year
        start_date = date(year, 1, 1)  # January 1st of the year
        end_date = date(year, 12, 31)  # December 31st of the year
        
        super().__init__(user_id=user_id, block_type='year', theme=theme)
        self.year = year
        self.start_date = start_date
        self.end_date = end_date
        # Additional attributes needed for YearBlock
        self.year_theme = theme
        self.goals = None
        self.goals_rationale = None
        self.rpe = None
        self.gains = None
        self.gratitudes = None
    
    @classmethod
    def get_or_create(cls, db: DBSession, user_id: int, year: int) -> 'YearBlock':
        """Get an existing year block or create a new one"""
        year_block = db.query(cls).filter_by(
            user_id=user_id,
            year=year
        ).first()
        
        if not year_block:
            year_block = cls(user_id=user_id, year=year)
            db.add(year_block)
            db.commit()
        
        return year_block
    
    def as_dict(self) -> Dict:
        """Convert the year block to a dictionary"""
        data = super().as_dict()
        data.update({
            'year': self.year,
            'year_theme': self.year_theme,
            'theme': self.theme,  # Keep for backward compatibility
            'goals': self.goals,
            'goals_rationale': self.goals_rationale,
            'why': self.goals_rationale,  # Include 'why' for consistency with frontend
            'rpe': self.rpe,
            'gains': self.gains,
            'gratitudes': self.gratitudes
        })
        return data 