from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Project
from .repository import ProjectRepository
from ..tasks.models import Task
from src.database.base.exceptions import ValidationError


class ProjectValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

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
            
        return self.repository.create(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            win_condition=data.get('win_condition'),
            reason=data.get('reason'),
            next_step=data.get('next_step'),
            active=True
        )

    def update_project(self, project: Project, data: Dict[str, Any]) -> Project:
        update_data = {}
        for field in ['title', 'description', 'win_condition', 'reason', 'next_step', 'active']:
            if field in data:
                update_data[field] = data[field]
        
        if 'title' in update_data and not update_data['title']:
            raise ProjectValidationError("Title cannot be empty")

        return self.repository.update(project, **update_data)

    def delete_project(self, project: Project) -> None:
        self.repository.delete(project)

    def get_project_tasks(self, project_id: int, user_id: int, include_completed: bool = False) -> List[Task]:
        return self.repository.get_project_tasks(project_id, user_id, include_completed)

    def create_task(self, project: Project, user_id: int, data: Dict[str, Any]) -> Task:
        if not data.get('title'):
            raise ProjectValidationError("Task title is required")

        task = Task(
            user_id=user_id,
            project_id=project.id,
            title=data['title'],
            description=data.get('description'),
            completed=False
        )
        self.repository.session.add(task)
        self.repository.session.commit()
        return task

    def update_task(self, task: Task, data: Dict[str, Any]) -> Task:
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'completed' in data:
            task.completed = data['completed']
            if data['completed']:
                task.completed_at = datetime.utcnow()

        self.repository.session.commit()
        return task

    def delete_task(self, task: Task) -> None:
        self.repository.session.delete(task)
        self.repository.session.commit()