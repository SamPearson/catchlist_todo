from typing import List, Optional, Dict
from .repository import TaskRepository
from .models import Task

class TaskService:
    """Service layer for task operations"""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, user_id: int, title: str) -> Task:
        """Create a new task"""
        return self.repository.create(user_id=user_id, title=title)

    def get_task(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a specific task, ensuring user ownership"""
        return self.repository.get(task_id=task_id, user_id=user_id)

    def list_tasks(self, user_id: int, include_completed: bool = False) -> List[Task]:
        """List all tasks for a user"""
        return self.repository.list_for_user(
            user_id=user_id,
            include_completed=include_completed
        )

    def update_task(self, task: Task, data: Dict) -> Task:
        """Update a task with the given data"""
        return self.repository.update(
            task,
            title=data.get('content'),
            completed=data.get('completed')
        )

    def delete_task(self, task: Task) -> None:
        """Delete a task"""
        self.repository.delete(task)

    def toggle_task_completion(self, task: Task) -> Task:
        """Toggle the completion status of a task"""
        if task.completed:
            return self.repository.mark_incomplete(task)
        return self.repository.mark_completed(task)

    def mark_completed(self, task: Task) -> Task:
        """Mark a task as completed"""
        return self.repository.mark_completed(task)

    def mark_incomplete(self, task: Task) -> Task:
        """Mark a task as incomplete"""
        return self.repository.mark_incomplete(task)
