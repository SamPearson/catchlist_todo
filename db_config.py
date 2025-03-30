import os
from sqlalchemy import inspect
from db_models import db


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///todo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add a secure secret key for JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-key-please-change-in-production')


def initialize_database(app):
    """Check and initialize the database only if not already created."""
    with app.app_context():
        inspector = inspect(db.engine)
        required_tables = {'todo', 'user'}
        existing_tables = set(inspector.get_table_names())
        
        if not required_tables.issubset(existing_tables):
            print("Creating Database")
            db.create_all()
            print("Database Created")
        else:
            print("Database already initialized")
