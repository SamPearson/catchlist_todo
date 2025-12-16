# This file can be empty 

# Import all route modules to ensure they're properly registered
from . import auth
#from . import routines
#from . import commitments
from .reports import reports_bp  # Use new structured reports module
#from . import catchlist_items
#from . import today
#from . import calendar_events
from . import tags