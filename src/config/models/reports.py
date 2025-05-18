from datetime import datetime, date
from typing import Dict, List, Optional, Union
from sqlalchemy.orm import Session
from .time_blocks import TimeBlock, DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from .commitment import Commitment
from .project import ProjectTask
from .catchlist import CatchlistItem
from .routines import Session as RoutineSession

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