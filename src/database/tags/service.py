from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.db import db
from src.database.tags.models import Tag
from .repository import TagRepository
from src.database.base.exceptions import ValidationError

class TagValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class TagService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = TagRepository(session)

    def get_tag(self, tag_id: int, user_id: int) -> Optional[Tag]:
        """Get a specific tag ensuring ownership"""
        return self.repository.get_by_id(tag_id, user_id)

    def get_all_by_user(self, user_id: int) -> list[Tag]:
        """Get all tags for a user"""
        return self.repository.get_all_by_user_id(user_id)

    def create_tag(self, name: str, user_id: int, color: str = '#6c757d') -> Tag:
        """Create a new tag"""
        name = (name or "").strip()
        if not name:
            raise TagValidationError("Tag name is required.")
        
        if self.repository.exists_by_name(name, user_id):
            raise TagValidationError(f"A tag with the name '{name}' already exists.")
        
        return self.repository.create(name, user_id, color)

    def update_tag(self, tag_id: int, user_id: int, name: Optional[str] = None, color: Optional[str] = None) -> \
    Optional[Tag]:
        """Update an existing tag"""
        if name is not None:
            name = name.strip()
            if not name:
                raise TagValidationError("Tag name cannot be empty.")

            if len(name) > 50:
                raise TagValidationError("Name cannot exceed 50 characters.")

            if self.repository.exists_by_name(name, user_id, exclude_id=tag_id):
                raise TagValidationError(f"A tag with the name '{name}' already exists.")

        if color is not None:
            color = color.strip()
            if color.startswith('#'):
                color = color[1:]
            if len(color) != 6:
                raise TagValidationError("Invalid color format. Use #RRGGBB.")

        return self.repository.update(tag_id, user_id, name, color)

    def delete_tag(self, tag_id: int, user_id: int) -> bool:
        """Delete a tag"""
        return self.repository.delete(tag_id, user_id)

    def add_tag_to_entity(self, tag_id: int, user_id: int, entity: any) -> bool:
        """Add a tag to any entity that supports tags"""
        from src.database.tags.models import TagAssociation

        tag = self.get_tag(tag_id, user_id)
        if not tag:
            return False

        if not hasattr(entity, 'tags'):
            raise TagValidationError(f"Entity {type(entity).__name__} does not support tags")

        # Check if association already exists
        existing = self.session.query(TagAssociation).filter_by(
            tag_id=tag.id,
            entity_id=entity.id,
            entity_type=entity.__class__.__name__.lower()
        ).first()

        if not existing:
            # Create association explicitly
            association = TagAssociation(
                tag_id=tag.id,
                entity_id=entity.id,
                entity_type=entity.__class__.__name__.lower()
            )
            self.session.add(association)
            self.session.commit()
        return True

    def remove_tag_from_entity(self, tag_id: int, user_id: int, entity: any) -> bool:
        """Remove a tag from any entity that supports tags"""
        from src.database.tags.models import TagAssociation
        
        tag = self.get_tag(tag_id, user_id)
        if not tag:
            return False

        if not hasattr(entity, 'tags'):
            raise TagValidationError(f"Entity {type(entity).__name__} does not support tags")

        # Directly delete the association instead of relying on relationship management
        association = self.session.query(TagAssociation).filter_by(
            tag_id=tag.id,
            entity_id=entity.id,
            entity_type=entity.__class__.__name__.lower()
        ).first()

        if association:
            self.session.delete(association)
            self.session.commit()
            return True
        else:
            raise TagValidationError(
                f"Tag '{tag.name}' is not attached to this {entity.__class__.__name__.lower()}"
            )
        
        return False