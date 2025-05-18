from datetime import datetime, date
from ...config.models import Commitment, db

def create_commitment_from_task(task, user_id):
    """
    Create a commitment from a project task.
    
    Args:
        task: ProjectTask instance
        user_id: ID of the user creating the commitment
    
    Returns:
        Commitment instance
    """
    commitment = Commitment(
        user_id=user_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        start_time=task.start_time,
        project_task_id=task.id,
        item_type='project_task'
    )
    
    db.session.add(commitment)
    db.session.commit()
    return commitment

def create_commitment_from_routine(routine, session, user_id):
    """
    Create a commitment from a routine session.
    
    Args:
        routine: Routine instance
        session: Session instance
        user_id: ID of the user creating the commitment
    
    Returns:
        Commitment instance
    """
    commitment = Commitment(
        user_id=user_id,
        due_date=session.start_time.date() if hasattr(session.start_time, 'date') else session.start_time,
        start_time=session.start_time,
        end_time=session.end_time,
        routine_id=routine.id,
        session_id=session.id
    )
    
    db.session.add(commitment)
    db.session.commit()
    return commitment

def create_commitment_from_catchlist_item(item, user_id):
    """
    Create a commitment from a catchlist item.
    
    Args:
        item: CatchlistItem instance
        user_id: ID of the user creating the commitment
    
    Returns:
        Commitment instance
    """
    commitment = Commitment(
        user_id=user_id,
        catchlist_item_id=item.id,
        due_date=date.today()
    )
    
    db.session.add(commitment)
    db.session.commit()
    return commitment 