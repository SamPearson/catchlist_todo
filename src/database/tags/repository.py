
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.tags.models import Tag

class TagRepository:
    """Repository for managing tag entities"""

    def __init__(self, db_session: Session):
        self.db_session = db_session


    def get_all_by_user_id(self, user_id: int) -> list[Tag]:
        """Retrieve all tags for a specific user"""
        return (
            self.db_session.query(Tag)
            .filter_by(user_id=user_id)
            .all()
        )

    def get_by_id(self, tag_id: int, user_id: int) -> Optional[Tag]:
        """Retrieve a specific tag by ID and user ID"""
        return (
            self.db_session.query(Tag)
            .filter_by(id=tag_id, user_id=user_id)
            .first()
        )


    def create(self, name: str, user_id: int, color: str = '#6c757d') -> Tag:
        """Create a new tag"""
        tag = Tag(
            name=name,
            color=color,
            user_id=user_id
        )
        self.db_session.add(tag)
        self.db_session.commit()
        return tag


    def update(self, tag_id: int, user_id: int, name: Optional[str] = None, color: Optional[str] = None) -> Optional[Tag]:
        """Update an existing tag"""
        tag = self.get_by_id(tag_id, user_id)
        if tag:
            if name is not None:
                tag.name = name
            if color is not None:
                tag.color = color
            self.db_session.commit()
        return tag


    def delete(self, tag_id: int, user_id: int) -> bool:
        """Delete a tag"""
        tag = self.get_by_id(tag_id, user_id)
        if tag:
            self.db_session.delete(tag)
            self.db_session.commit()
            return True
        return False