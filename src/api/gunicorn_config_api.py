from src.api.api import app
from src.config.db_models import db
from src.config.db_config import initialize_database

def on_starting(server):
    with app.app_context():
        db.create_all()  # This ensures tables exist
        initialize_database(app)  # This handles any other initialization