"""
Database migration script to add new columns to execution tables
"""
import sqlite3
import os
from pathlib import Path

# Get the database path
config_dir = Path(__file__).parent
instance_db_path = config_dir.parent.parent / 'instance' / 'catchlist_todo.db'

def run_migration():
    print(f"Looking for database at: {instance_db_path}")
    
    # Check if database file exists
    if not os.path.exists(instance_db_path):
        print(f"Error: Database file not found at {instance_db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(instance_db_path)
        cursor = conn.cursor()
        
        # Get existing columns in event_execution
        cursor.execute("PRAGMA table_info(event_execution)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add user_id column if it doesn't exist
        if 'user_id' not in column_names:
            print("Adding user_id column to event_execution table...")
            cursor.execute("ALTER TABLE event_execution ADD COLUMN user_id INTEGER")
            
            # Set user_id based on related CalendarEvent's user_id
            cursor.execute("""
                UPDATE event_execution 
                SET user_id = (
                    SELECT user_id 
                    FROM calendar_event 
                    WHERE calendar_event.id = event_execution.event_id
                )
            """)
            print("Updated event_execution records with user_id from related calendar_event")
        else:
            print("user_id column already exists in event_execution table")
        
        # Add attempted column if it doesn't exist
        if 'attempted' not in column_names:
            print("Adding attempted column to event_execution table...")
            cursor.execute("ALTER TABLE event_execution ADD COLUMN attempted BOOLEAN DEFAULT 1")
            print("Added attempted column with default value of True")
        else:
            print("attempted column already exists in event_execution table")
            
        # Check for completed column
        if 'completed' not in column_names:
            print("Adding completed column to event_execution table...")
            cursor.execute("ALTER TABLE event_execution ADD COLUMN completed BOOLEAN")
            
            # Set completed based on 'completed' field
            cursor.execute("""
                UPDATE event_execution 
                SET completed = CASE WHEN completed = 'yes' THEN 1 ELSE 0 END
            """)
            print("Added completed column and migrated data")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration() 