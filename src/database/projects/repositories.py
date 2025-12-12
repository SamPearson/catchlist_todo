from typing import List, Optional, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .models import Project
from ..tasks.models import Task

T = TypeVar('T', Project, Task)

class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, project_id: int, user_id: int) -> Optional[Project]:
        return self.session.query(Project).filter(
            and_(
                Project.id == project_id,
                Project.user_id == user_id
            )
        ).first()

    def get_all_by_user(self, user_id: int, include_completed: bool = False) -> List[Project]:
        query = self.session.query(Project).filter(Project.user_id == user_id)
        if not include_completed:
            query = query.filter(Project.active.is_(True))
        return list(query) #May result in a type hint warning due to a sqlalchemy quirk


    def get_project_tasks(self, project_id: int, user_id: int, include_completed: bool = False) -> List[Task]:
        """Get all tasks associated with a specific project"""
        query = self.session.query(Task).join(Project).filter(
            and_(
                Project.id == project_id,
                Project.user_id == user_id,
                Task.project_id == project_id
            )
        )

        if not include_completed:
            query = query.filter(Task.completed.is_(False))

        return list(query)

    def get_task_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        return self.session.query(Task).join(Project).filter(
            and_(
                Task.id == task_id,
                Project.user_id == user_id,
                Task.project_id.isnot(None)  # Ensure it's a project task
            )
        ).first()

    def get_today_tasks(self, user_id: int, today) -> List[Task]:
        query = self.session.query(Task).join(Project).filter(
            and_(
                Project.user_id == user_id,
                Task.project_id.isnot(None)  # Ensure it's a project task
            )
        )
        return list(query) #May result in a type hint warning due to a sqlalchemy quirk