from datetime import date
from typing import List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from .models import DayReport, WeekReport, MonthReport, SeasonReport, YearReport

T = TypeVar('T', DayReport, WeekReport, MonthReport, SeasonReport, YearReport)

class ReportRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, model_class: Type[T], **filters) -> Optional[T]:
        """Generic get method for any report type"""
        return self.session.query(model_class).filter_by(**filters).first()

    def create(self, model_class: Type[T], **data) -> T:
        """Generic create method for any report type"""
        report = model_class(**data)
        self.session.add(report)
        self.session.commit()
        return report

    def update(self, report: T, **data) -> T:
        """Generic update method for any report type"""
        for key, value in data.items():
            setattr(report, key, value)
        self.session.commit()
        return report

    def delete(self, report: T) -> bool:
        """Generic delete method for any report type"""
        self.session.delete(report)
        self.session.commit()
        return True

    def list(self, model_class: Type[T], **filters) -> List[T]:
        """Generic list method for any report type"""
        return self.session.query(model_class).filter_by(**filters).all()