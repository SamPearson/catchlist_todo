import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database.base.exceptions import ValidationError, EntityNotFoundError
from .models import Principle, PrincipleAssociation
from .repository import PrincipleRepo


class PrincipleValidationError(ValidationError):
    pass


class PrincipleService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PrincipleRepo(session)

    def get_principle(self, principle_id: int, user_id: int) -> Optional[Principle]:
        return self.repo.get(principle_id, user_id)

    def list_principles(self, user_id: int) -> List[Principle]:
        return self.repo.list_for_user(user_id)

    def create_principle(self, user_id: int, data: Dict[str, Any]) -> Principle:
        title = (data.get('title') or "").strip()
        if not title:
            raise PrincipleValidationError("Principle title is required.")

        if len(title) > 50:
            raise PrincipleValidationError("Name cannot exceed 50 characters.")

        if self.repo.exists_by_title(title, user_id):
            raise PrincipleValidationError(f"A tag with the name '{title}' already exists.")

        if 'color' in data:
            color = data['color'].strip()
            if color.startswith('#'):
                color = color[1:]
            if len(color) != 6:
                raise PrincipleValidationError("Invalid color format. Use #RRGGBB.")
            data['color'] = color


        return self.repo.create(
            user_id=user_id,
            title=title,
            description=data.get('description'),
            reason=data.get('reason'),
            color=data.get('color', 'ffd700')
        )

    def update_principle(self, principle_id: int, user_id: int, data: Dict[str, Any]) -> Optional[Principle]:
        principle = self.get_principle(principle_id, user_id)
        if not principle:
            raise EntityNotFoundError(f"Principle with ID {principle_id} not found.")

        update_data = {}

        if 'title' in data:
            update_title = data['title']
            if not update_title.strip():
                raise PrincipleValidationError("Title cannot be empty.")
            update_data['title'] = update_title.strip()

            if self.repo.exists_by_title(update_title, user_id):
                raise PrincipleValidationError(f"A tag with the name '{update_title}' already exists.")

            if len(update_title) > 50:
                raise PrincipleValidationError("Name cannot exceed 50 characters.")

        if 'color' in data:
            color = data['color']
            if color.startswith('#'):
                color = color[1:]
            if len(color) != 6:
                raise PrincipleValidationError(f"Invalid color format '{color}'. Use #RRGGBB.")
            update_data['color'] = color


        if 'description' in data:
            update_data['description'] = data['description']
        if 'reason' in data:
            update_data['reason'] = data['reason']

        return self.repo.update(principle, **update_data)

    def delete_principle(self, principle_id: int, user_id: int) -> bool:
        principle = self.get_principle(principle_id, user_id)
        if not principle:
            return False
        return self.repo.delete(principle)

    def attach_to_entity(self, principle_id: int, user_id: int, entity: Any) -> bool:
        from .models import PrincipleAssociation
    
        principle = self.get_principle(principle_id, user_id)
        if not principle:
            raise EntityNotFoundError(f"Principle with ID {principle_id} not found.")
        if not hasattr(entity, 'principles'):
            logging.error(f"Entity {entity} does not support principles.\n{entity.__dict__}")
            raise PrincipleValidationError(f"Entity {entity} does not support principles.")

        # Check if association already exists
        existing = self.session.query(PrincipleAssociation).filter_by(
            principle_id=principle.id,
            entity_id=entity.id,
            entity_type=entity.__class__.__name__.lower()
        ).first()

        if not existing:
            # Create association explicitly
            association = PrincipleAssociation(
                principle_id=principle.id,
                entity_id=entity.id,
                entity_type=entity.__class__.__name__.lower()
            )
            self.session.add(association)
            self.session.commit()
        return True

    def detach_from_entity(self, principle_id: int, user_id: int, entity: Any) -> bool:

        principle = self.get_principle(principle_id, user_id)
        if not principle:
            raise EntityNotFoundError(f"Principle with ID {principle_id} not found.")


        # Directly delete the association instead of relying on relationship management
        association = self.session.query(PrincipleAssociation).filter_by(
            principle_id=principle.id,
            entity_id=entity.id,
            entity_type=entity.__class__.__name__.lower()
        ).first()

        if association:
            self.session.delete(association)
            self.session.commit()
            return True
        
        return False