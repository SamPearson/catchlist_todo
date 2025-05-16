from flask import Flask
from .db_config import Config
from .models import db
import logging
from sqlalchemy import text, inspect

def run_migrations():
    """Run database migrations for schema changes"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if the active column exists in calendar_event table
            result = db.session.execute(text("SELECT 1 FROM pragma_table_info('calendar_event') WHERE name='active'")).fetchone()
            
            if not result:
                logging.info("Adding 'active' column to calendar_event table")
                # Add the active column with default value of True
                db.session.execute(text("ALTER TABLE calendar_event ADD COLUMN active BOOLEAN DEFAULT 1"))
                db.session.commit()
                logging.info("Successfully added 'active' column")
            else:
                logging.info("'active' column already exists in calendar_event table")
            
            # Check if the check_in_count column exists in event_execution table
            result = db.session.execute(text("SELECT 1 FROM pragma_table_info('event_execution') WHERE name='check_in_count'")).fetchone()
            
            if not result:
                logging.info("Adding 'check_in_count' column to event_execution table")
                # Add the check_in_count column with default value of 0
                db.session.execute(text("ALTER TABLE event_execution ADD COLUMN check_in_count INTEGER DEFAULT 0"))
                db.session.commit()
                logging.info("Successfully added 'check_in_count' column")
            else:
                logging.info("'check_in_count' column already exists in event_execution table")
            
            # Check if the on_daily_todo column exists in catchlist_entry table
            result = db.session.execute(text("SELECT 1 FROM pragma_table_info('catchlist_entry') WHERE name='on_daily_todo'")).fetchone()
            
            if not result:
                logging.info("Adding 'on_daily_todo' column to catchlist_entry table")
                # Add the on_daily_todo column with default value of False
                db.session.execute(text("ALTER TABLE catchlist_entry ADD COLUMN on_daily_todo BOOLEAN DEFAULT 0"))
                db.session.commit()
                logging.info("Successfully added 'on_daily_todo' column")
            else:
                logging.info("'on_daily_todo' column already exists in catchlist_entry table")
                
            # Check if the completed column exists in catchlist_entry table
            result = db.session.execute(text("SELECT 1 FROM pragma_table_info('catchlist_entry') WHERE name='completed'")).fetchone()
            
            if not result:
                logging.info("Adding 'completed' column to catchlist_entry table")
                # Add the completed column with default value of False
                db.session.execute(text("ALTER TABLE catchlist_entry ADD COLUMN completed BOOLEAN DEFAULT 0"))
                db.session.commit()
                logging.info("Successfully added 'completed' column")
            else:
                logging.info("'completed' column already exists in catchlist_entry table")
                
            # Check if the completed_at column exists in catchlist_entry table
            result = db.session.execute(text("SELECT 1 FROM pragma_table_info('catchlist_entry') WHERE name='completed_at'")).fetchone()
            
            if not result:
                logging.info("Adding 'completed_at' column to catchlist_entry table")
                # Add the completed_at column as nullable
                db.session.execute(text("ALTER TABLE catchlist_entry ADD COLUMN completed_at TIMESTAMP"))
                db.session.commit()
                logging.info("Successfully added 'completed_at' column")
            else:
                logging.info("'completed_at' column already exists in catchlist_entry table")
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error during migration: {str(e)}")
            raise e

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations() 