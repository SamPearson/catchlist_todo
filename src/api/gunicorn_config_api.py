from src.api.api import app
from src.config.db_config import initialize_database


def on_starting(server):
    initialize_database(app)
