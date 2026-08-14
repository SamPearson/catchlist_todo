from typing import Optional
from sqlalchemy.orm import Session
from src.database.base.base_repositories import UserOwnedRepository
from src.database.tags.tag_models import Tag


class TagRepository(UserOwnedRepository[Tag]):
    """Repository for managing tag entities"""

    def __init__(self, db_session: Session):
        super().__init__(session=db_session, model_class=Tag)

    def get_all_by_user_id(self, user_id: int) -> list[Tag]:
        """Retrieve all tags for a specific user"""
        return (
            self.session.query(Tag)
            .filter_by(user_id=user_id)
            .all()
        )

    def get_by_name(self, name: str, user_id: int) -> Optional[Tag]:
        """Retrieve a tag by name for a specific user"""
        return (
            self.session.query(Tag)
            .filter_by(name=name, user_id=user_id)
            .first()
        )

    def exists_by_name(self, name: str, user_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if a tag with the given name exists for a user"""
        query = self.session.query(Tag).filter_by(name=name, user_id=user_id)
        if exclude_id is not None:
            query = query.filter(Tag.id != exclude_id)
        return query.first() is not None

    def create(self, name: str, user_id: int, color: str = '#6c757d') -> Tag:
        """Create a new tag"""
        tag = Tag(
            name=name,
            color=color,
            user_id=user_id
        )
        self.session.add(tag)
        self.session.commit()
        return tag

    def update(self, user_id: int, tag_id: int, name: Optional[str] = None, color: Optional[str] = None) -> Tag:
        """Update an existing tag"""
        data = {}
        if name is not None:
            data['name'] = name
        if color is not None:
            data['color'] = color
        return super().update(user_id, tag_id, **data)

    def delete(self, user_id: int, tag_id: int) -> bool:
        """Delete a tag"""
        return super().delete(user_id, tag_id)
