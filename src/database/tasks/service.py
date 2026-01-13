from typing import List, Optional, Dict
from datetime import datetime
from .repository import TaskRepository
from .models import Task
from src.database.base.exceptions import ValidationError


class TaskValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


VALID_STATUSES = {'open', 'waiting', 'deferred', 'declined', 'stale'}


class TaskService:
    """Service layer for task operations"""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, user_id: int, title: str, data: Optional[Dict] = None) -> Task:
        """Create a new task"""
        normalized = (title or "").strip()
        if not normalized:
            raise TaskValidationError("title is required.")
        
        data = data or {}
        status = data.get('status', 'open')
        if status not in VALID_STATUSES:
            raise TaskValidationError(f"Invalid status: {status}. Must be one of: {', '.join(VALID_STATUSES)}")
        
        return self.repository.create(
            user_id=user_id,
            title=normalized,
            description=data.get('description'),
            status=status,
            active=data.get('active', True),
            project_id=data.get('project_id')
        )

    def get_task(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a specific task, ensuring user ownership"""
        return self.repository.get(id=task_id, user_id=user_id)

    def list_tasks(self, user_id: int, include_completed: bool = False) -> List[Task]:
        """List all tasks for a user"""
        return self.repository.list_for_user(
            user_id=user_id,
            include_completed=include_completed
        )

    def update_task(self, task: Task, data: Dict) -> Task:
        """Update a task with the given data (excluding completion status)"""
        if "title" in data:
            title = str(data.get("title") or "").strip()
            if not title:
                raise TaskValidationError("title cannot be empty.")
        else:
            title = None

        if "content" in data and "title" not in data:
            raise TaskValidationError("content is deprecated; use title.")
        
        if "status" in data and data["status"] not in VALID_STATUSES:
            raise TaskValidationError(f"Invalid status: {data['status']}. Must be one of: {', '.join(VALID_STATUSES)}")

        return self.repository.update(
            task,
            title=title,
            description=data.get("description"),
            status=data.get("status"),
            active=data.get("active"),
            project_id=data.get("project_id")
        )

    def delete_task(self, task: Task) -> None:
        """Delete a task"""
        self.repository.delete(task)

    def complete_task(self, task: Task) -> Task:
        """Mark a task as completed with timestamp"""
        if task.completed:
            return task
        return self.repository.mark_completed(task)

    def uncomplete_task(self, task: Task) -> Task:
        """Mark a task as not completed, clearing timestamp"""
        if not task.completed:
            return task
        return self.repository.mark_incomplete(task)

    def toggle_task_completion(self, task: Task) -> Task:
        """Toggle the completion status of a task"""
        if task.completed:
            return self.uncomplete_task(task)
        return self.complete_task(task)

    # Keep these for backwards compatibility, delegating to new methods
    def mark_completed(self, task: Task) -> Task:
        """Mark a task as completed"""
        return self.complete_task(task)

    def mark_incomplete(self, task: Task) -> Task:
        """Mark a task as incomplete"""
        return self.uncomplete_task(task)


    def attach_to_project(self, task: Task, project_id: int) -> Task:
        """Attach a task to a project"""
        return self.repository.set_project(task, project_id)

    def detach_from_project(self, task: Task) -> Task:
        """Detach a task from its project (make it standalone)"""
        return self.repository.set_project(task, None)

