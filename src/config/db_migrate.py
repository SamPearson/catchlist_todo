from flask import Flask
from .db_config import Config
from .db_models import db
import logging

def run_migrations():
    """Run database migrations for schema changes"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if the active column exists in calendar_event table
            result = db.session.execute("SELECT 1 FROM pragma_table_info('calendar_event') WHERE name='active'").fetchone()
            
            if not result:
                logging.info("Adding 'active' column to calendar_event table")
                # Add the active column with default value of True
                db.session.execute("ALTER TABLE calendar_event ADD COLUMN active BOOLEAN DEFAULT 1")
                db.session.commit()
                logging.info("Successfully added 'active' column")
            else:
                logging.info("'active' column already exists in calendar_event table")
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error during migration: {str(e)}")
            raise e

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations() 