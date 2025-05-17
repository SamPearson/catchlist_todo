from datetime import datetime, date, timedelta
from ..db_setup import db
from sqlalchemy.orm import foreign

class TimeBlock(db.Model):
    __tablename__ = 'time_block'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Polymorphic discriminator
    block_type = db.Column(db.String(50), nullable=False)
    
    # Common fields
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    journal_entry = db.Column(db.Text)
    sleep_hours = db.Column(db.Float)
    rpe = db.Column(db.Integer)  # Rating of perceived exertion (1-10)
    
    # Common time-related fields
    year = db.Column(db.Integer)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship(
        'Comment',
        primaryjoin="and_(Comment.entity_type=='time_block', foreign(Comment.entity_id)==TimeBlock.id)",
        back_populates="time_block",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    __mapper_args__ = {
        'polymorphic_on': block_type,
        'polymorphic_identity': 'time_block'
    }
    
    def linked_commitments(self):
        """Get all commitments that fall within this time block's date range"""
        from .commitment import Commitment
        return Commitment.query.filter(
            Commitment.user_id == self.user_id,
            Commitment.due_date >= self.start_date,
            Commitment.due_date <= self.end_date
        ).all()
    
    def as_dict(self):
        return {
            "id": self.id,
            "block_type": self.block_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "journal_entry": self.journal_entry,
            "sleep_hours": self.sleep_hours,
            "rpe": self.rpe,
            "year": self.year,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class DayBlock(TimeBlock):
    __mapper_args__ = {
        'polymorphic_identity': 'day'
    }
    
    # Day-specific fields can be added here
    mood = db.Column(db.String(50))
    
    def __init__(self, user_id, date, **kwargs):
        """Initialize a DayBlock for a specific date"""
        super().__init__(
            user_id=user_id,
            start_date=date,
            end_date=date,
            block_type='day',
            **kwargs
        )
    
    def as_dict(self):
        data = super().as_dict()
        data.update({
            "mood": self.mood
        })
        return data


class WeekBlock(TimeBlock):
    __mapper_args__ = {
        'polymorphic_identity': 'week'
    }
    
    # Week-specific fields
    week_number = db.Column(db.Integer)
    
    def __init__(self, user_id, start_date, **kwargs):
        """Initialize a WeekBlock starting on a specific date"""
        # Calculate the end date (start_date + 6 days)
        end_date = start_date + timedelta(days=6)
        week_number = start_date.isocalendar()[1]
        
        super().__init__(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            block_type='week',
            week_number=week_number,
            **kwargs
        )
    
    def as_dict(self):
        data = super().as_dict()
        data.update({
            "week_number": self.week_number
        })
        return data


class MonthBlock(TimeBlock):
    __mapper_args__ = {
        'polymorphic_identity': 'month'
    }
    
    # Month-specific fields
    month_number = db.Column(db.Integer)
    
    def __init__(self, user_id, year, month, **kwargs):
        """Initialize a MonthBlock for a specific year/month"""
        # Calculate start and end dates for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        super().__init__(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            block_type='month',
            month_number=month,
            year=year,
            **kwargs
        )
    
    def as_dict(self):
        data = super().as_dict()
        data.update({
            "month_number": self.month_number
        })
        return data


class SeasonBlock(TimeBlock):
    __mapper_args__ = {
        'polymorphic_identity': 'season'
    }
    
    # Season-specific fields
    season_name = db.Column(db.String(20))  # Spring, Summer, Fall, Winter
    
    def __init__(self, user_id, year, season_name, **kwargs):
        """Initialize a SeasonBlock for a specific year/season"""
        # Define season dates based on meteorological seasons
        seasons = {
            'Winter': (date(year, 12, 1), date(year+1, 3, 1) - timedelta(days=1)),
            'Spring': (date(year, 3, 1), date(year, 6, 1) - timedelta(days=1)),
            'Summer': (date(year, 6, 1), date(year, 9, 1) - timedelta(days=1)),
            'Fall': (date(year, 9, 1), date(year, 12, 1) - timedelta(days=1))
        }
        
        if season_name not in seasons:
            raise ValueError(f"Invalid season: {season_name}")
        
        start_date, end_date = seasons[season_name]
        
        super().__init__(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            block_type='season',
            season_name=season_name,
            year=year,
            **kwargs
        )
    
    def as_dict(self):
        data = super().as_dict()
        data.update({
            "season_name": self.season_name
        })
        return data


class YearBlock(TimeBlock):
    __mapper_args__ = {
        'polymorphic_identity': 'year'
    }
    
    def __init__(self, user_id, year, **kwargs):
        """Initialize a YearBlock for a specific year"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        super().__init__(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            block_type='year',
            year=year,
            **kwargs
        )
    
    # No need to override as_dict since we're just using the parent's year field 