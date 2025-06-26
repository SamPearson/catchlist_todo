# blocks/service.py
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from ..dates.services import DateService


class BlockService:
    def __init__(self, session: Session):
        self.session = session
        self.date_service = DateService()

    def get_or_create_block(self, user_id: int, report_date: date, block_type: str):
        """Get or create the appropriate time block based on type"""
        if block_type == 'week':
            year, week_num, _ = report_date.isocalendar()
            return self._get_or_create_week_block(user_id, year, week_num)
        elif block_type == 'month':
            return self._get_or_create_month_block(user_id, report_date.year, report_date.month)
        elif block_type == 'season':
            season = self.date_service.get_season_from_date(report_date)
            return self._get_or_create_season_block(user_id, report_date.year, season)
        elif block_type == 'year':
            return self._get_or_create_year_block(user_id, report_date.year)
        else:
            raise ValueError(f"Invalid block type: {block_type}")

    def _get_or_create_week_block(self, user_id: int, year: int, week_num: int):
        """Get or create a week block"""
        block = self.block_model.query.filter_by(
            user_id=user_id,
            year=year,
            week=week_num
        ).first()

        if not block:
            block = self.block_model(user_id=user_id, year=year, week=week_num)
            self.session.add(block)
            self.session.commit()

        return block

    # Similar methods for other block types...