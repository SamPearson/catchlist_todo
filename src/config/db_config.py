import os
from sqlalchemy import inspect
from .db_setup import db
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask

config_dir = Path(__file__).parent
load_dotenv(os.path.join(config_dir, '.env')) 

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///catchlist_todo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Add a secure secret key for JWT
    try:
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        if not JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY not found in environment variables")
    except Exception as e:
        print("ERROR: JWT_SECRET_KEY must be set in .env file")
        print("Please create a .env file in src/config with JWT_SECRET_KEY=your_secret_key")
        raise e
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    @staticmethod
    def get_token_expires_delta():
        return timedelta(hours=12)


def initialize_database(app):
    """Initialize the database with all tables if they don't exist"""
    with app.app_context():
        db.create_all()
        
        # Run migrations for schema changes
        try:
            from .db_migrate import run_migrations
            run_migrations()
        except Exception as e:
            print(f"Error running migrations: {str(e)}")
