"""Database models for the application.""" 

from flask_sqlalchemy import SQLAlchemy
from ..db_setup import db

# Import all models
from .user import User, BlacklistedToken
from .project import Project, ProjectTask
from .catchlist import CatchlistItem
from .routines import Routine, Session
from .commitment import Commitment
from .time_blocks import TimeBlock, DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from .checkin import Checkin
from .reports import Report, DayReport, WeekReport, MonthReport, SeasonReport, YearReport, ReportGenerator
from .tags import Tag, RoutineTag, SessionTag, ProjectTag, ProjectTaskTag, CatchlistItemTag

# Define __all__ to control what gets imported with "from models import *"
__all__ = [
    'Report', 'DayReport', 'WeekReport', 'MonthReport', 'SeasonReport', 'YearReport', 'ReportGenerator',
    'TimeBlock', 'DayBlock', 'WeekBlock', 'MonthBlock', 'SeasonBlock', 'YearBlock',
    'Commitment', 'Project', 'ProjectTask', 'CatchlistItem', 'Routine', 'Session', 'Checkin', 'db',
    'Tag', 'RoutineTag', 'SessionTag', 'ProjectTag', 'ProjectTaskTag', 'CatchlistItemTag'
] 