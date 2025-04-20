import os
from sqlalchemy import inspect
from .db_setup import db
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///todo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add a secure secret key for JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-key-please-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)  # Set tokens to expire after 1 day

    @classmethod
    def get_token_expires_delta(cls):
        """Single source of truth for token expiration"""
        return cls.JWT_ACCESS_TOKEN_EXPIRES


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
