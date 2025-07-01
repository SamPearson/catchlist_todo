"""Database models for the application.""" 

from flask_sqlalchemy import SQLAlchemy
from ..db_setup import db

# Import all models
from .user import User, BlacklistedToken
from .project import Project, ProjectTask
from .catchlist import CatchlistItem
from .routines import Routine, Session
from .commitment import Commitment, SoftCommitment
from .time_blocks import TimeBlock, DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from .checkin import Checkin
from .tags import LegacyTag, RoutineTag, SessionTag, ProjectTag, ProjectTaskTag, CatchlistItemTag
from .calendar import Calendar

# Define __all__ to control what gets imported with "from models import *"
__all__ = [
    'User', 'BlacklistedToken',
    'Project', 'ProjectTask',
    'CatchlistItem',
    'Routine', 'Session',
    'Commitment', 'SoftCommitment',
    'TimeBlock', 'DayBlock', 'WeekBlock', 'MonthBlock', 'SeasonBlock', 'YearBlock',
    'Checkin',
    'LegacyTag', 'RoutineTag', 'SessionTag', 'ProjectTag', 'ProjectTaskTag', 'CatchlistItemTag',
    'Calendar',
    'db'
] 