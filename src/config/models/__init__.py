"""Database models for the application.""" 

from flask_sqlalchemy import SQLAlchemy
from ..db_setup import db

# Import all models
from .user import User, BlacklistedToken
from .project import Project, ProjectTask
from .catchlist import CatchlistItem
from .time_blocks import TimeBlock, DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from .routines import Routine, Session
from .checkin import Checkin
from .commitment import Commitment
from .comment import Comment

# Import legacy models that we'll keep for now
from .legacy import ProjectSubtask, CalendarEvent, EventExecution, BaseExecution, TaskExecution

# Define __all__ to control what gets imported with "from models import *"
__all__ = [
    'db',
    'User', 'BlacklistedToken',
    'Project', 'ProjectTask',
    'CatchlistItem',
    'TimeBlock', 'DayBlock', 'WeekBlock', 'MonthBlock', 'SeasonBlock', 'YearBlock',
    'Routine', 'Session', 'Checkin',
    'Commitment',
    'Comment',
    # Legacy models
    'ProjectSubtask', 'CalendarEvent', 'EventExecution',
    'BaseExecution', 'TaskExecution'
] 