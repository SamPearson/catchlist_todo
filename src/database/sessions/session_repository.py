from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from src.database.base.base_repositories import UserOwnedRepository
from .session_models import RoutineSession as RoutineSession
from src.database.principles.principle_models import PrincipleAssociation, Principle
from src.database.tags.tag_models import TagAssociation, Tag


class SessionRepo(UserOwnedRepository[RoutineSession]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=RoutineSession)

    def list_for_window(self, user_id: int, start: datetime, end: datetime) -> List[RoutineSession]:
        """Find all sessions for a user within a specific time window"""
        return (
            self.session.query(RoutineSession)
            .filter(
                RoutineSession.user_id == user_id,
                RoutineSession.start_time >= start,
                RoutineSession.start_time < end
            )
            .order_by(RoutineSession.start_time.asc())
            .all()
        )

    def list_for_window_filtered(
            self,
            user_id: int,
            start: datetime,
            end: datetime,
            statuses: List[str] = None,
            tag_names: List[str] = None,
            principle_names: List[str] = None,
            routine_id: int = None
    ) -> List[RoutineSession]:
        """Find sessions with optional filters. All filters are combined with AND logic."""

        query = self.session.query(RoutineSession).filter(
            RoutineSession.user_id == user_id,
            RoutineSession.start_time >= start,
            RoutineSession.start_time < end
        )

        if statuses:
            query = query.filter(RoutineSession.status.in_(statuses))

        if routine_id:
            query = query.filter(RoutineSession.routine_id == routine_id)

        if tag_names:
            query = (
                query.join(TagAssociation, RoutineSession.id == TagAssociation.entity_id)
                .join(Tag, Tag.id == TagAssociation.tag_id)
                .filter(
                    TagAssociation.entity_type == 'routinesession',
                    Tag.name.in_(tag_names)
                )
            )

        if principle_names:
            query = (
                query.join(PrincipleAssociation, RoutineSession.id == PrincipleAssociation.entity_id)
                .join(Principle, Principle.id == PrincipleAssociation.principle_id)
                .filter(
                    PrincipleAssociation.entity_type == 'routinesession',
                    Principle.title.in_(principle_names)
                )
            )

        return query.order_by(RoutineSession.start_time.asc()).distinct().all()