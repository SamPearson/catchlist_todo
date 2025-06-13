# Import all view modules to ensure they're properly registered

# This makes the modules available for import from the views package
from . import day_reports
from . import week_reports
from . import month_reports
from . import season_reports
from . import year_reports
