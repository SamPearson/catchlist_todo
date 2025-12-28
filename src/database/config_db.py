import os
from sqlalchemy import inspect
from src.database.db import db
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask
import logging



config_dir = Path(__file__).parent
load_dotenv(os.path.join(config_dir, '.env'))

class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    INSTANCE_DIR = BASE_DIR / "instance"
    DB_PATH = INSTANCE_DIR / "catchlist_todo.db"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        f"sqlite:///{DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Load JWT secret key from environment
    try:
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        if not JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY not found in environment variables")
    except Exception as e:
        logging.error("JWT_SECRET_KEY must be set in .env file")
        logging.error("Please create a .env file in src/config with JWT_SECRET_KEY=your_secret_key")
        raise e

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    @staticmethod
    def get_token_expires_delta():
        return timedelta(hours=12)


def initialize_database(app):
    """Initialize the database with all tables if they don't exist"""
    with app.app_context():
        logging.info("Starting Database Initialization")

        # Print tables before creation
        logging.debug("Tables in metadata before creation:")
        for table in db.metadata.tables:
            logging.debug("- %s", table)

        logging.info("Creating tables...")
        db.create_all()

        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        logging.debug("Actual tables in database: %s", tables)

        logging.info("Database Initialization Complete")