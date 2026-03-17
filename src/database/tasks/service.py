from typing import List, Optional, Dict
from .repository import TaskRepository
from .models import Task
from src.database.base.exceptions import ValidationError
from src.database.checkins.service import CheckinService
from src.database.db import db


class TaskValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


VALID_STATUSES = {'open', 'waiting', 'deferred', 'declined', 'stale'}
MAX_TITLE_LENGTH = 200


class TaskService:
    """Service layer for task operations"""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, user_id: int, title: str, data: Optional[Dict] = None) -> Task:
        """Create a new task"""
        normalized = (title or "").strip()
        if not normalized:
            raise TaskValidationError("title is required.")

        if len(normalized) > MAX_TITLE_LENGTH:
            raise TaskValidationError(f"title cannot exceed {MAX_TITLE_LENGTH} characters.")

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
        # Check for disallowed fields
        disallowed_fields = {'status', 'active', 'completed', 'completed_at', 'project_id'}
        provided_disallowed = disallowed_fields.intersection(data.keys())
        if provided_disallowed:
            raise TaskValidationError(
                f"Cannot update {', '.join(sorted(provided_disallowed))} via update_task. Use dedicated methods instead."
            )
        
        if "title" in data:
            title = str(data.get("title") or "").strip()
            if not title:
                raise TaskValidationError("title cannot be empty.")
            if len(title) > MAX_TITLE_LENGTH:
                raise TaskValidationError(f"title cannot exceed {MAX_TITLE_LENGTH} characters.")
        else:
            title = None

        if "content" in data and "title" not in data:
            raise TaskValidationError("content is deprecated; use title.")

        return self.repository.update(
            task,
            title=title,
            description=data.get("description")
        )

    def delete_task(self, task: Task) -> None:
        """Delete a task and cascade delete all associated records"""

        
        # Delete all checkins for this task
        checkin_service = CheckinService(db.session)
        checkin_service.delete_for_target(
            user_id=task.user_id,
            target_type='task',
            target_id=task.id,
        )
        
        # Delete all tag associations for this task
        from src.database.tags.models import TagAssociation
        db.session.query(TagAssociation).filter_by(
            entity_id=task.id,
            entity_type='task',
        ).delete()
        
        # Delete all principle associations for this task
        from src.database.principles.models import PrincipleAssociation
        db.session.query(PrincipleAssociation).filter_by(
            entity_id=task.id,
            entity_type='task',
        ).delete()
        
        # Commit association deletions
        db.session.commit()
        
        # Delete the task itself
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

    def activate_task(self, task: Task) -> Task:
        """Activate a task (set active=true)"""
        if task.active:
            return task
        return self.repository.update(task, active=True)

    def deactivate_task(self, task: Task) -> Task:
        """Deactivate a task (set active=false)"""
        if not task.active:
            return task
        return self.repository.update(task, active=False)

    def change_status(self, task: Task, new_status: str) -> Task:
        """Change a task's status"""
        if new_status not in VALID_STATUSES:
            raise TaskValidationError(f"Invalid status: {new_status}. Must be one of: {', '.join(VALID_STATUSES)}")
        
        if task.status == new_status:
            return task
        
        return self.repository.update(task, status=new_status)

    def attach_to_project(self, task: Task, project_id: int, user_id: int) -> Task:
        """Attach a task to a project with ownership validation"""
        from src.database.projects.repository import ProjectRepository
        from src.database.db import db

        project_repo = ProjectRepository(db.session)
        project = project_repo.get(id=project_id, user_id=user_id)

        if not project:
            raise TaskValidationError(f"Project not found or access denied")

        return self.repository.set_project(task, project_id)

    def detach_from_project(self, task: Task) -> Task:
        """Detach a task from its project (make it standalone)"""
        return self.repository.set_project(task, None)

