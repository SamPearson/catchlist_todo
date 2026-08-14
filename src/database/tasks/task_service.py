from typing import List, Optional, Dict
from .task_repository import TaskRepository
from .task_models import Task
from src.database.base.exceptions import ValidationError
from src.database.checkins.checkin_service import CheckinService
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
        
        # Create the task without project association
        task = self.repository.create(
            user_id=user_id,
            title=normalized,
            description=data.get('description'),
            status=status,
            active=data.get('active', True),
            project_id=None
        )
        
        # If project_id provided, attach it using the existing validation logic
        project_id = data.get('project_id')
        if project_id is not None:
            task = self.attach_to_project(user_id, task.id, project_id)
        
        return task

    def get_task(self, user_id: int, task_id: int) -> Task:
        """Get a specific task, ensuring user ownership"""
        return self.repository.get(user_id, task_id)

    def list_tasks(self, user_id: int, include_completed: bool = False) -> List[Task]:
        """List all tasks for a user"""
        return self.repository.list_for_user(
            user_id=user_id,
            include_completed=include_completed
        )

    def update_task(self, user_id: int, task_id: int, data: Dict) -> Task:
        """Update a task with the given data (excluding completion status)"""
        # Fetch first so EntityNotFoundError is raised before any business logic runs
        self.repository.get(user_id, task_id)

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
            user_id,
            task_id,
            title=title,
            description=data.get("description")
        )

    def delete_task(self, user_id: int, task_id: int) -> None:
        """Delete a task and cascade delete all associated records"""

        # This will raise EntityNotFoundError if this task doesn't exist or isnt owned by this user,
        # handle that exception at the api layer
        task = self.repository.get(user_id, task_id)

        
        # Delete all checkins for this task
        checkin_service = CheckinService(db.session)
        checkin_service.delete_for_target(
            user_id=user_id,
            target_type='task',
            target_id=task_id,
        )
        
        # Delete all tag associations for this task
        from src.database.tags.tag_models import TagAssociation
        db.session.query(TagAssociation).filter_by(
            entity_id=task_id,
            entity_type='task',
        ).delete()
        
        # Delete all principle associations for this task
        from src.database.principles.principle_models import PrincipleAssociation
        db.session.query(PrincipleAssociation).filter_by(
            entity_id=task_id,
            entity_type='task',
        ).delete()

        # Delete the task itself
        self.repository.delete(user_id, task_id)

        # Commit association deletions
        db.session.commit()
        


    def complete_task(self, user_id: int, task_id: int) -> Task:
        """Mark a task as completed with timestamp"""
        task = self.repository.get(user_id, task_id)
        if task.completed:
            return task
        return self.repository.mark_completed(user_id, task_id)

    def uncomplete_task(self, user_id: int, task_id: int) -> Task:
        """Mark a task as not completed, clearing timestamp"""
        task = self.repository.get(user_id, task_id)
        if not task.completed:
            return task
        return self.repository.mark_incomplete(user_id, task_id)

    def toggle_task_completion(self, user_id: int, task_id: int) -> Task:
        """Toggle the completion status of a task"""
        task = self.repository.get(user_id, task_id)
        if task.completed:
            return self.uncomplete_task(user_id, task_id)
        return self.complete_task(user_id, task_id)

    def activate_task(self, user_id: int, task_id: int) -> Task:
        """Activate a task (set active=true)"""
        task = self.repository.get(user_id, task_id)
        if task.active:
            return task
        return self.repository.update(user_id, task_id, active=True)

    def deactivate_task(self, user_id: int, task_id: int) -> Task:
        """Deactivate a task (set active=false)"""
        task = self.repository.get(user_id, task_id)
        if not task.active:
            return task
        return self.repository.update(user_id, task_id, active=False)

    def change_status(self, user_id: int, task_id: int, new_status: str) -> Task:
        """Change a task's status"""
        if new_status not in VALID_STATUSES:
            raise TaskValidationError(f"Invalid status: {new_status}. Must be one of: {', '.join(VALID_STATUSES)}")
        
        task = self.repository.get(user_id, task_id)
        if task.status == new_status:
            return task
        
        return self.repository.update(user_id, task_id, status=new_status)

    def attach_to_project(self, user_id: int, task_id: int, project_id: int) -> Task:
        """Attach a task to a project with ownership validation"""
        from src.database.projects.project_repository import ProjectRepository
        from src.database.db import db

        # Raises EntityNotFoundError if the task is missing or unowned
        self.repository.get(user_id, task_id)

        project_repo = ProjectRepository(db.session)
        # Raises EntityNotFoundError if the project is missing or unowned
        project_repo.get(user_id, project_id)

        return self.repository.set_project(user_id, task_id, project_id)

    def detach_from_project(self, user_id: int, task_id: int) -> Task:
        """Detach a task from its project (make it standalone)"""
        self.repository.get(user_id, task_id)
        return self.repository.set_project(user_id, task_id, None)

