
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.db import db
from src.database.tags.models import Tag
from .repository import TagRepository

class TagService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = TagRepository(session)

    def get_all_by_user(self, user_id: int) -> list[Tag]:
        """Get all tags for a user"""
        return self.repository.get_all_by_user_id(user_id)

    def create_tag(self, name: str, user_id: int, color: str = '#6c757d') -> Tag:
        """Create a new tag"""
        return self.repository.create(name, user_id, color)

    def update_tag(self, tag_id: int, user_id: int, name: Optional[str] = None, color: Optional[str] = None) -> Optional[Tag]:
        """Update an existing tag"""
        return self.repository.update(tag_id, user_id, name, color)

    def delete_tag(self, tag_id: int, user_id: int) -> bool:
        """Delete a tag"""
        return self.repository.delete(tag_id, user_id)

    def add_tag_to_entity(self, tag_id: int, user_id: int, entity: any) -> bool:
        """Add a tag to any entity that supports tags"""
        tag = self.repository.get_by_id(tag_id, user_id)
        if not tag:
            return False

        if not hasattr(entity, 'tags'):
            raise AttributeError(f"Entity {type(entity).__name__} does not support tags")

        if tag not in entity.tags:
            entity.tags.append(tag)
            self.session.commit()
        return True

    def remove_tag_from_entity(self, tag_id: int, user_id: int, entity: any) -> bool:
        """Remove a tag from any entity that supports tags"""
        tag = self.repository.get_by_id(tag_id, user_id)
        if not tag:
            return False

        if not hasattr(entity, 'tags'):
            raise AttributeError(f"Entity {type(entity).__name__} does not support tags")

        if tag in entity.tags:
            entity.tags.remove(tag)
            self.session.commit()
        return True