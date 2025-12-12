from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Task

class TaskRepository:
    """Repository for handling Task database operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, title: str) -> Task:
        """Create a new task"""
        task = Task(user_id=user_id, title=title)
        self.session.add(task)
        self.session.commit()
        return task

    def get(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a specific task by ID and user_id"""
        return Task.query.filter_by(
            id=task_id,
            user_id=user_id
        ).first()

    def list_for_user(self, user_id: int, include_completed: bool = False) -> List[Task]:
        """List all tasks for a user"""
        query = Task.query.filter_by(user_id=user_id)
        if not include_completed:
            query = query.filter_by(completed=False)
        return query.order_by(Task.created_at.desc()).all()

    def update(self, task: Task, title: Optional[str] = None, completed: Optional[bool] = None) -> Task:
        """Update a task"""
        if title is not None:
            task.content = title
        if completed is not None:
            task.completed = completed
        self.session.commit()
        return task

    def delete(self, task: Task) -> None:
        """Delete a task"""
        self.session.delete(task)
        self.session.commit()

    def mark_completed(self, task: Task) -> Task:
        """Mark a task as completed"""
        return self.update(task, completed=True)

    def mark_incomplete(self, task: Task) -> Task:
        """Mark a task as incomplete"""
        return self.update(task, completed=False)