from flask import Flask
import logging
from sqlalchemy import text
from datetime import datetime
from .db_config import Config
from .db_setup import db

# Import both old and new models
from .models.legacy import Todo, CatchListEntry, ProjectSubtask, CalendarEvent, EventExecution
from .models import (CatchlistItem, ProjectTask, Routine, Session, 
                    Checkin, Commitment, DayBlock, TimeBlock)

def run_schema_migrations():
    """Create the new tables in the database"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            logging.info("Creating new tables")
            # Create new tables
            db.create_all()
            logging.info("Successfully created new tables")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating new tables: {str(e)}")
            raise e

def migrate_todos_to_catchlist():
    """Migrate data from old Todo model to new CatchlistItem model"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            logging.info("Migrating todos to catchlist items")
            todos = Todo.query.all()
            for todo in todos:
                # Check if already migrated
                existing = CatchlistItem.query.filter_by(
                    content=todo.title,
                    user_id=todo.user_id
                ).first()
                
                if not existing:
                    # Create a new CatchlistItem
                    catchlist_item = CatchlistItem(
                        content=todo.title,
                        user_id=todo.user_id,
                        completed=todo.complete,
                        completed_at=datetime.utcnow() if todo.complete else None,
                        status='completed' if todo.complete else 'active'
                    )
                    db.session.add(catchlist_item)
            
            db.session.commit()
            logging.info(f"Migrated {len(todos)} todos to catchlist items")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error migrating todos: {str(e)}")
            raise e

def migrate_catchlist_entries():
    """Migrate data from old CatchListEntry model to new CatchlistItem model"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            logging.info("Migrating catchlist entries to catchlist items")
            entries = CatchListEntry.query.all()
            for entry in entries:
                # Check if already migrated
                existing = CatchlistItem.query.filter_by(
                    content=entry.content,
                    user_id=entry.user_id
                ).first()
                
                if not existing:
                    # Create a new CatchlistItem
                    catchlist_item = CatchlistItem(
                        content=entry.content,
                        user_id=entry.user_id,
                        completed=entry.completed,
                        completed_at=entry.completed_at,
                        status=entry.status,
                        created_at=entry.created_at
                    )
                    db.session.add(catchlist_item)
            
            db.session.commit()
            logging.info(f"Migrated {len(entries)} catchlist entries to catchlist items")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error migrating catchlist entries: {str(e)}")
            raise e

def migrate_project_subtasks():
    """Migrate data from old ProjectSubtask model to new ProjectTask model"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            logging.info("Migrating project subtasks to project tasks")
            subtasks = ProjectSubtask.query.all()
            for subtask in subtasks:
                # Check if already migrated
                existing = ProjectTask.query.filter_by(
                    title=subtask.title,
                    project_id=subtask.project_id
                ).first()
                
                if not existing:
                    # Create a new ProjectTask
                    project_task = ProjectTask(
                        title=subtask.title,
                        project_id=subtask.project_id,
                        complete=subtask.complete,
                        created_at=datetime.utcnow(),
                        updated_at=subtask.updated_at
                    )
                    db.session.add(project_task)
                    
                    # If the subtask was on the daily todo, create a commitment for today
                    if subtask.on_daily_todo and not subtask.complete:
                        from datetime import date
                        commitment = Commitment(
                            user_id=db.session.query(ProjectSubtask, 'user_id').join(
                                'project').filter(ProjectSubtask.id == subtask.id).first()[0],
                            task_id=project_task.id,
                            entity_type='project_task',
                            due_date=date.today(),
                            completed=False
                        )
                        db.session.add(commitment)
            
            db.session.commit()
            logging.info(f"Migrated {len(subtasks)} project subtasks to project tasks")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error migrating project subtasks: {str(e)}")
            raise e

def migrate_calendar_events():
    """Migrate data from old CalendarEvent model to new Routine and Session models"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            logging.info("Migrating calendar events to routines and sessions")
            events = CalendarEvent.query.all()
            for event in events:
                # Check if already migrated
                existing = Routine.query.filter_by(
                    external_uid=event.uid,
                    user_id=event.user_id
                ).first()
                
                if not existing:
                    # Create a new Routine
                    routine = Routine(
                        title=event.summary,
                        description=event.description,
                        rrule=event.rrule,
                        active=event.active,
                        user_id=event.user_id,
                        external_uid=event.uid,
                        external_source='calendar'
                    )
                    db.session.add(routine)
                    db.session.flush()  # Flush to get the routine.id
                    
                    # Create a Session for this specific instance
                    session = Session(
                        routine_id=routine.id,
                        start_time=event.start_time,
                        end_time=event.end_time,
                        notes=event.description
                    )
                    db.session.add(session)
                    
                    # Migrate any existing executions
                    executions = EventExecution.query.filter_by(event_id=event.id).all()
                    for execution in executions:
                        # Create a Checkin for each execution
                        checkin = Checkin(
                            session_id=session.id,
                            timestamp=execution.execution_date,
                            notes=execution.notes,
                            rpe=execution.rpe
                        )
                        db.session.add(checkin)
            
            db.session.commit()
            logging.info(f"Migrated {len(events)} calendar events to routines and sessions")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error migrating calendar events: {str(e)}")
            raise e

def create_day_blocks():
    """Create DayBlock entries for days with activity"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            logging.info("Creating day blocks for days with activity")
            
            # Get all unique dates with event executions
            query = text("""
                SELECT DISTINCT user_id, execution_date 
                FROM event_execution 
                WHERE execution_date IS NOT NULL
            """)
            result = db.session.execute(query)
            
            # Create DayBlocks for each date
            count = 0
            for row in result:
                user_id = row[0]
                exec_date = row[1]
                
                # Check if already exists
                existing = DayBlock.query.filter_by(
                    user_id=user_id,
                    start_date=exec_date
                ).first()
                
                if not existing:
                    # Create a new DayBlock
                    day_block = DayBlock(
                        user_id=user_id,
                        date=exec_date
                    )
                    db.session.add(day_block)
                    count += 1
            
            db.session.commit()
            logging.info(f"Created {count} day blocks")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating day blocks: {str(e)}")
            raise e


def run_all_migrations():
    """Run all migration functions in the correct order"""
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting database migrations for new models")
    
    # First create the schema
    run_schema_migrations()
    
    # Then migrate the data
    migrate_todos_to_catchlist()
    migrate_catchlist_entries()
    migrate_project_subtasks()
    migrate_calendar_events()
    create_day_blocks()
    
    logging.info("Completed all migrations successfully")


if __name__ == "__main__":
    run_all_migrations() 