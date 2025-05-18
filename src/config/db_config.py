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
    # Always use the absolute path to the instance directory
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    INSTANCE_DIR = BASE_DIR / "instance"
    DB_PATH = INSTANCE_DIR / "catchlist_todo.db"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        f"sqlite:///{DB_PATH}"
    )
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
        # Print the actual database URI being used
        print("DB URI in use:", app.config['SQLALCHEMY_DATABASE_URI'])
        # Import all models to ensure they're registered with SQLAlchemy
        from .models import db
        
        # Force recreate all tables
        db.drop_all()
        db.create_all()
        
        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Created tables:", tables)
