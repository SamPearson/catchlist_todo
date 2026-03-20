from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.base.repositories import UserOwnedRepository
from .models import Project
from ..tasks.models import Task


class ProjectRepository(UserOwnedRepository[Project]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Project)

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

        return query.all()

    def get_task_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a task by ID ensuring it belongs to a project owned by the user"""
        return (
            self.session.query(Task)
            .join(Project)
            .filter(
                and_(
                    Task.id == task_id,
                    Project.user_id == user_id,
                    Task.project_id.isnot(None)
                )
            )
            .first()
        )