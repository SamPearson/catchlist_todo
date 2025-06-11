from flask import Blueprint

# Create the main reports blueprint
reports_bp = Blueprint('reports', __name__)

# Import individual report type modules
from .views import day_reports, week_reports, month_reports, season_reports, year_reports

# Register nested blueprints
reports_bp.register_blueprint(day_reports.bp)
reports_bp.register_blueprint(week_reports.bp)
reports_bp.register_blueprint(month_reports.bp)
reports_bp.register_blueprint(season_reports.bp)
reports_bp.register_blueprint(year_reports.bp)

# Import shared routes
from .views import shared
