
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class DayReport:
    date: date
    cleaning_adherence: Optional[float] = None
    created_at: Optional[datetime] = None
    diet_adherence: Optional[float] = None
    distractions_rating: Optional[int] = None
    drugs_rating: Optional[int] = None
    gains: Optional[str] = None
    gains_rating: Optional[int] = None
    gratitudes: Optional[str] = None
    notes: Optional[str] = None
    prayer_rating: Optional[int] = None
    sleep_hours: Optional[float] = None
    updated_at: Optional[datetime] = None
    work_adherence: Optional[float] = None
    work_rpe: Optional[int] = None


class DayReportFactory:
    @classmethod
    def create(cls, **kwargs) -> DayReport:
        """Create a new DayReport with default or specified values"""
        return DayReport(
            date=kwargs.get('date', date.today()),
            **kwargs
        )