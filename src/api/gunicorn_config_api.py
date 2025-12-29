from src.api.api import app
from src.database.db import db
from src.database.config_db import initialize_database

def on_starting(server):
    with app.app_context():
        db.create_all()  # This ensures tables exist
        initialize_database(app)  # This handles any other initialization