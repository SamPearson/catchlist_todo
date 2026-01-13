from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.base.repositories import UserOwnedRepository
from .models import Task


class TaskRepository(UserOwnedRepository[Task]):
    """Repository for handling Task database operations"""

    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Task)

    def create(self, user_id: int, title: str, description: Optional[str] = None,
               status: str = 'open', active: bool = True, 
               project_id: Optional[int] = None) -> Task:
        """Create a new task"""
        return super().create(
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            active=active,
            project_id=project_id,
            completed=False
        )

    def list_for_user(self, user_id: int, include_completed: bool = False, **filters) -> List[Task]:
        """List all tasks for a user"""
        if not include_completed:
            filters['completed'] = False
        tasks = super().list_for_user(user_id, **filters)
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def update(self, task: Task, title: Optional[str] = None, 
               description: Optional[str] = None, status: Optional[str] = None,
               active: Optional[bool] = None, project_id: Optional[int] = None,
               completed: Optional[bool] = None, completed_at: Optional[datetime] = None) -> Task:
        """Update a task - only sets fields that are explicitly provided"""
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if status is not None:
            update_data['status'] = status
        if active is not None:
            update_data['active'] = active
        if project_id is not None:
            update_data['project_id'] = project_id
        if completed is not None:
            update_data['completed'] = completed
        if completed_at is not None or (completed is not None and not completed):
            # Set completed_at if provided, or clear it if uncompleting
            update_data['completed_at'] = completed_at
        
        return super().update(task, **update_data)

    def mark_completed(self, task: Task) -> Task:
        """Mark a task as completed with timestamp"""
        return super().update(task, completed=True, completed_at=datetime.utcnow())

    def mark_incomplete(self, task: Task) -> Task:
        """Mark a task as incomplete, clearing timestamp"""
        return super().update(task, completed=False, completed_at=None)