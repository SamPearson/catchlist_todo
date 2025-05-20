from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import func
from .time_blocks import TimeBlock, DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from .commitment import Commitment
from .project import ProjectTask
from .catchlist import CatchlistItem
from .routines import Session as RoutineSession
from . import db, Checkin

class Report:
    """Base class for all reports"""
    
    def __init__(self, time_block: TimeBlock, db: Session):
        self.time_block = time_block
        self.db = db
        self._commitments = None
        self._stats = None
    
    @property
    def commitments(self) -> List[Commitment]:
        """Get all commitments for this time period"""
        if self._commitments is None:
            self._commitments = self.time_block.linked_commitments(self.db)
        return self._commitments
    
    @property
    def stats(self) -> Dict:
        """Calculate basic statistics for the report"""
        if self._stats is None:
            total = len(self.commitments)
            completed = sum(1 for c in self.commitments if c.completed)
            completion_rate = (completed / total * 100) if total > 0 else 0
            
            # Calculate average RPE from checkins
            rpe_values = []
            for commitment in self.commitments:
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
        return self._stats
    
    def as_dict(self) -> Dict:
        """Convert report to dictionary format"""
        return {
            "time_block": self.time_block.as_dict(),
            "stats": self.stats,
            "commitments": [c.as_dict() for c in self.commitments]
        }


class DayReport(Report):
    """Report for a single day"""
    
    def __init__(self, day_block: DayBlock, db: Session):
        super().__init__(day_block, db)
        self.day_block = day_block
    
    @property
    def stats(self) -> Dict:
        stats = super().stats
        stats.update({
            "sleep_hours": self.day_block.sleep_hours,
            "mood": self.day_block.mood,
            "rpe": self.day_block.rpe
        })
        return stats


class WeekReport(Report):
    """Report for a week"""
    
    def __init__(self, week_block: WeekBlock, db: Session):
        super().__init__(week_block, db)
        self.week_block = week_block
    
    @property
    def stats(self) -> Dict:
        stats = super().stats
        stats.update({
            "weekly_aim": self.week_block.weekly_aim,
            "weekly_notes": self.week_block.weekly_notes
        })
        return stats


class MonthReport(Report):
    """Report for a month"""
    
    def __init__(self, month_block: MonthBlock, db: Session):
        super().__init__(month_block, db)
        self.month_block = month_block
    
    @property
    def stats(self) -> Dict:
        stats = super().stats
        stats.update({
            "theme": self.month_block.theme
        })
        return stats


class SeasonReport(Report):
    """Report for a season"""
    
    def __init__(self, season_block: SeasonBlock, db: Session):
        super().__init__(season_block, db)
        self.season_block = season_block
    
    @property
    def stats(self) -> Dict:
        stats = super().stats
        stats.update({
            "aim": self.season_block.aim
        })
        return stats


class YearReport(Report):
    """Report for a year"""
    
    def __init__(self, year_block: YearBlock, db: Session):
        super().__init__(year_block, db)
        self.year_block = year_block
    
    @property
    def stats(self) -> Dict:
        stats = super().stats
        stats.update({
            "theme": self.year_block.theme
        })
        return stats 


class ReportGenerator:
    @staticmethod
    def generate_missing_reports(user_id: int, db: Session):
        """Generate any missing reports for the user"""
        today = date.today()
        
        # Check last 7 days
        for i in range(7):
            check_date = today - timedelta(days=i)
            day_block = DayBlock.get_or_create(db, user_id, check_date.year, check_date.month, check_date.day)
            
            # Generate day report if missing
            if not day_block.report_generated:
                ReportGenerator.generate_day_report(day_block, db)
        
        # Check last 4 weeks
        for i in range(4):
            check_date = today - timedelta(weeks=i)
            week_number = check_date.isocalendar()[1]
            week_block = WeekBlock.get_or_create(db, user_id, check_date.year, week_number)
            
            # Generate week report if missing
            if not week_block.report_generated:
                ReportGenerator.generate_week_report(week_block, db)
    
    @staticmethod
    def generate_day_report(day_block: DayBlock, db: Session):
        """Generate a day report from raw data"""
        # Get all checkins for the day
        checkins = db.query(Checkin).filter(
            Checkin.user_id == day_block.user_id,
            func.date(Checkin.timestamp) == day_block.start_date
        ).all()
        
        # Calculate metrics
        rpe_values = [c.rpe for c in checkins if c.rpe is not None]
        mood_values = [c.mood for c in checkins if c.mood is not None]
        energy_values = [c.energy for c in checkins if c.energy is not None]
        
        # Update day block
        day_block.rpe = sum(rpe_values) / len(rpe_values) if rpe_values else None
        day_block.mood = sum(mood_values) / len(mood_values) if mood_values else None
        day_block.energy = sum(energy_values) / len(energy_values) if energy_values else None
        day_block.report_generated = True
        
        db.commit()
    
    @staticmethod
    def generate_week_report(week_block: WeekBlock, db: Session):
        """Generate a week report from daily reports"""
        # Get all day blocks for the week
        day_blocks = db.query(DayBlock).filter(
            DayBlock.user_id == week_block.user_id,
            DayBlock.start_date >= week_block.start_date,
            DayBlock.start_date <= week_block.end_date
        ).all()
        
        # Calculate metrics
        rpe_values = [d.rpe for d in day_blocks if d.rpe is not None]
        mood_values = [d.mood for d in day_blocks if d.mood is not None]
        
        # Update week block
        week_block.rpe = sum(rpe_values) / len(rpe_values) if rpe_values else None
        week_block.mood = sum(mood_values) / len(mood_values) if mood_values else None
        week_block.report_generated = True
        
        db.commit()
    
    @staticmethod
    def generate_month_report(month_block: MonthBlock, db: Session):
        """Generate a month report from weekly reports"""
        # Get all week blocks for the month
        week_blocks = db.query(WeekBlock).filter(
            WeekBlock.user_id == month_block.user_id,
            WeekBlock.start_date >= month_block.start_date,
            WeekBlock.end_date <= month_block.end_date
        ).all()
        
        # Calculate metrics
        rpe_values = [w.rpe for w in week_blocks if w.rpe is not None]
        mood_values = [w.mood for w in week_blocks if w.mood is not None]
        
        # Update month block
        month_block.rpe = sum(rpe_values) / len(rpe_values) if rpe_values else None
        month_block.mood = sum(mood_values) / len(mood_values) if mood_values else None
        month_block.report_generated = True
        
        db.commit()
    
    @staticmethod
    def generate_season_report(season_block: SeasonBlock, db: Session):
        """Generate a season report from monthly reports"""
        # Get all month blocks for the season
        month_blocks = db.query(MonthBlock).filter(
            MonthBlock.user_id == season_block.user_id,
            MonthBlock.start_date >= season_block.start_date,
            MonthBlock.end_date <= season_block.end_date
        ).all()
        
        # Calculate metrics
        rpe_values = [m.rpe for m in month_blocks if m.rpe is not None]
        mood_values = [m.mood for m in month_blocks if m.mood is not None]
        
        # Update season block
        season_block.rpe = sum(rpe_values) / len(rpe_values) if rpe_values else None
        season_block.mood = sum(mood_values) / len(mood_values) if mood_values else None
        season_block.report_generated = True
        
        db.commit()
    
    @staticmethod
    def generate_year_report(year_block: YearBlock, db: Session):
        """Generate a year report from seasonal reports"""
        # Get all season blocks for the year
        season_blocks = db.query(SeasonBlock).filter(
            SeasonBlock.user_id == year_block.user_id,
            SeasonBlock.start_date >= year_block.start_date,
            SeasonBlock.end_date <= year_block.end_date
        ).all()
        
        # Calculate metrics
        rpe_values = [s.rpe for s in season_blocks if s.rpe is not None]
        mood_values = [s.mood for s in season_blocks if s.mood is not None]
        
        # Update year block
        year_block.rpe = sum(rpe_values) / len(rpe_values) if rpe_values else None
        year_block.mood = sum(mood_values) / len(mood_values) if mood_values else None
        year_block.report_generated = True
        
        db.commit() 