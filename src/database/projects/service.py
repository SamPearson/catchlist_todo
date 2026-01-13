from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Project
from .repository import ProjectRepository
from ..tasks.models import Task
from ..tasks.service import TaskService
from ..tasks.repository import TaskRepository
from src.database.base.exceptions import ValidationError


class ProjectValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


VALID_STATUSES = {'open', 'waiting', 'deferred', 'declined', 'stale'}


class ProjectService:
    def __init__(self, repository: ProjectRepository, task_service: TaskService = None):
        self.repository = repository
        # Allow injection or create from same session
        self._task_service = task_service

    @property
    def task_service(self) -> TaskService:
        if self._task_service is None:
            task_repo = TaskRepository(self.repository.session)
            self._task_service = TaskService(task_repo)
        return self._task_service

    def get_project(self, project_id: int, user_id: int) -> Optional[Project]:
        return self.repository.get(project_id, user_id)

    def list_projects(self, user_id: int, include_completed: bool = False) -> List[Project]:
        filters = {}
        if not include_completed:
            filters['active'] = True
        return self.repository.list_for_user(user_id, **filters)

    def create_project(self, user_id: int, data: Dict[str, Any]) -> Project:
        if not data.get('title'):
            raise ProjectValidationError("Project title is required")
        
        status = data.get('status', 'open')
        if status not in VALID_STATUSES:
            raise ProjectValidationError(f"Invalid status: {status}. Must be one of: {', '.join(VALID_STATUSES)}")
            
        return self.repository.create(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            win_condition=data.get('win_condition'),
            reason=data.get('reason'),
            next_step=data.get('next_step'),
            status=status,
            active=data.get('active', True),
            completed=False
        )

    def update_project(self, project: Project, data: Dict[str, Any]) -> Project:
        update_data = {}
        for field in ['title', 'description', 'win_condition', 'reason', 'next_step', 'active', 'status']:
            if field in data:
                update_data[field] = data[field]
        
        if 'title' in update_data and not update_data['title']:
            raise ProjectValidationError("Title cannot be empty")
        
        if 'status' in update_data and update_data['status'] not in VALID_STATUSES:
            raise ProjectValidationError(f"Invalid status: {update_data['status']}. Must be one of: {', '.join(VALID_STATUSES)}")

        return self.repository.update(project, **update_data)

    def complete_project(self, project: Project) -> Project:
        """
        Mark a project as completed.
        - Fails if there are incomplete subtasks
        - Sets completed=True, completed_at=now, active=False
        """
        if project.completed:
            return project  # Already completed, no-op

        incomplete_tasks = [t for t in project.tasks if not t.completed]
        if incomplete_tasks:
            raise ProjectValidationError("Cannot complete project with incomplete subtasks")

        return self.repository.update(
            project,
            completed=True,
            completed_at=datetime.utcnow(),
            active=False
        )

    def uncomplete_project(self, project: Project) -> Project:
        """
        Mark a project as not completed.
        - Clears completed and completed_at
        - Does NOT automatically set active=True (user decides)
        """
        if not project.completed:
            return project  # Already not completed, no-op

        return self.repository.update(
            project,
            completed=False,
            completed_at=None
        )

    def delete_project(self, project: Project) -> None:
        self.repository.delete(project)

    def get_project_tasks(self, project_id: int, user_id: int, include_completed: bool = False) -> List[Task]:
        return self.repository.get_project_tasks(project_id, user_id, include_completed)

    def create_subtask(self, project: Project, user_id: int, title: str, data: Optional[Dict[str, Any]] = None) -> Task:
        """Create a task as a subtask of this project."""
        data = data or {}
        data['project_id'] = project.id
        return self.task_service.create_task(user_id, title, data)

    def add_task_to_project(self, project: Project, task: Task) -> Task:
        """Associate an existing task with this project."""
        return self.task_service.update_task(task, {'project_id': project.id})

    def remove_task_from_project(self, task: Task) -> Task:
        """Remove a task's project association (make it standalone)."""
        return self.task_service.update_task(task, {'project_id': None})