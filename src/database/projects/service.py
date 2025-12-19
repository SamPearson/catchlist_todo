from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Project
from .repository import ProjectRepository
from ..tasks.models import Task


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def get_project(self, project_id: int, user_id: int) -> Optional[Project]:
        return self.repository.get_by_id(project_id, user_id)

    def list_projects(self, user_id: int, include_completed: bool = False) -> List[Project]:
        return self.repository.get_all_by_user(user_id, include_completed)

    def create_project(self, user_id: int, data: Dict[str, Any]) -> Project:
        project = Project(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            win_condition=data.get('win_condition'),
            reason=data.get('reason'),
            next_step=data.get('next_step'),
            active=True
        )
        self.repository.session.add(project)
        self.repository.session.commit()
        return project

    def update_project(self, project: Project, data: Dict[str, Any]) -> Project:
        if 'title' in data:
            project.title = data['title']
        if 'description' in data:
            project.description = data['description']
        if 'win_condition' in data:
            project.win_condition = data['win_condition']
        if 'reason' in data:
            project.reason = data['reason']
        if 'next_step' in data:
            project.next_step = data['next_step']
        if 'active' in data:
            project.active = data['active']

        self.repository.session.commit()
        return project

    def delete_project(self, project: Project) -> None:
        self.repository.session.delete(project)
        self.repository.session.commit()

    def get_project_tasks(self, project_id: int, user_id: int, include_completed: bool = False) -> List[Task]:
        """Get all tasks associated with a specific project"""
        return self.repository.get_project_tasks(project_id, user_id, include_completed)

    def create_task(self, project: Project, user_id: int, data: Dict[str, Any]) -> Task:
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
        """Delete a task associated with a project"""
        self.repository.session.delete(task)
        self.repository.session.commit()