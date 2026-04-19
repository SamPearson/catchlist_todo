import os
from sqlalchemy import inspect
from src.database.db import db
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask
import logging

# Note: .env file is now in src/api/config/ 
# This config only handles database settings
# For JWT and API settings, see src/api/config/config.py

class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    INSTANCE_DIR = BASE_DIR / "instance"
    DB_PATH = INSTANCE_DIR / "catchlist_todo.db"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        f"sqlite:///{DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


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