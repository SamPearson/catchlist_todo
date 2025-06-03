# Model Interfaces and Mixins

## Overview
This document describes the common interfaces and mixins used across the application's data models. These interfaces ensure consistent behavior and reduce code duplication.

## TrackableMixin

### Purpose
Provides standard fields and methods for entities that can be tracked, monitored, and reported on.

### Implementation

```python
class TrackableMixin:
    """Mixin for models that can be tracked with checkins and comments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

    @property
    def entity_type(self):
        """Return the entity type for polymorphic relationships"""
        return self.__tablename__

    def get_comments(self):
        """Get all comments for this entity"""
        from .comment_models import Comment
        return Comment.query.filter(
            Comment.entity_type == self.entity_type,
            Comment.entity_id == self.id
        ).order_by(Comment.timestamp.desc()).all()

    def add_comment(self, user_id, content):
        """Add a comment to this entity"""
        from .comment_models import Comment
        comment = Comment(
            entity_type=self.entity_type,
            entity_id=self.id,
            user_id=user_id,
            content=content
        )
        db.session.add(comment)
        return comment

    def get_checkins(self):
        """Get all checkins for this entity"""
        from .execution_models import Checkin
        return Checkin.query.filter(
            Checkin.entity_type == self.entity_type,
            Checkin.entity_id == self.id
        ).order_by(Checkin.timestamp.desc()).all()

    def add_checkin(self, user_id, note=None, metrics=None):
        """Add a checkin to this entity"""
        from .execution_models import Checkin
        checkin = Checkin(
            entity_type=self.entity_type,
            entity_id=self.id,
            user_id=user_id,
            note=note,
            metrics=metrics or {}
        )
        db.session.add(checkin)
        return checkin
```

### Usage

Apply to any model that needs tracking capabilities:

```python
class CatchlistItem(db.Model, TrackableMixin):
    __tablename__ = 'catchlist_items'

    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)

    # TrackableMixin provides:
    # - id, user_id, created_at, updated_at, status
    # - get_comments(), add_comment()
    # - get_checkins(), add_checkin()
```

## CommitmentTrackingMixin

### Purpose
Extends TrackableMixin for entities that can have commitments (time-bound promises to work on them).

### Implementation

```python
class CommitmentTrackingMixin(TrackableMixin):
    """Mixin for models that can have commitments"""

    def get_commitments(self, timeframe=None):
        """Get commitments for this entity, optionally filtered by timeframe"""
        from .commitment_models import Commitment
        query = Commitment.query.filter(
            Commitment.entity_type == self.entity_type,
            Commitment.entity_id == self.id
        )

        if timeframe:
            query = query.filter(
                Commitment.due_date >= timeframe.start_date,
                Commitment.due_date <= timeframe.end_date
            )

        return query.order_by(Commitment.due_date).all()

    def add_commitment(self, due_date, user_id, time_box=None):
        """Add a commitment for this entity"""
        from .commitment_models import Commitment
        commitment = Commitment(
            entity_type=self.entity_type,
            entity_id=self.id,
            user_id=user_id,
            due_date=due_date,
            time_box=time_box
        )
        db.session.add(commitment)
        return commitment

    def complete_commitment(self, commitment_id):
        """Mark a specific commitment as completed"""
        from .commitment_models import Commitment
        commitment = Commitment.query.filter(
            Commitment.id == commitment_id,
            Commitment.entity_type == self.entity_type,
            Commitment.entity_id == self.id
        ).first()

        if commitment:
            commitment.completed = True
            commitment.completed_at = datetime.utcnow()
            return True
        return False
```

### Usage

```python
class ProjectTask(db.Model, CommitmentTrackingMixin):
    __tablename__ = 'project_tasks'

    content = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    # ...

    # CommitmentTrackingMixin provides:
    # - All TrackableMixin features
    # - get_commitments(), add_commitment(), complete_commitment()
```

## TaggableMixin

### Purpose
Enables models to have tags associated with them.

### Implementation

```python
class TaggableMixin:
    """Mixin for models that can be tagged"""

    @property
    def entity_type(self):
        """Return the entity type for polymorphic relationships"""
        return self.__tablename__

    def get_tags(self):
        """Get all tags for this entity"""
        from .tag_models import Tag, TagAssociation
        return Tag.query.join(TagAssociation, Tag.id == TagAssociation.tag_id).filter(
            TagAssociation.entity_type == self.entity_type,
            TagAssociation.entity_id == self.id
        ).all()

    def add_tag(self, tag_id):
        """Add a tag to this entity"""
        from .tag_models import TagAssociation
        # Check if association already exists
        existing = TagAssociation.query.filter(
            TagAssociation.tag_id == tag_id,
            TagAssociation.entity_type == self.entity_type,
            TagAssociation.entity_id == self.id
        ).first()

        if not existing:
            association = TagAssociation(
                tag_id=tag_id,
                entity_type=self.entity_type,
                entity_id=self.id
            )
            db.session.add(association)
            return association
        return existing

    def remove_tag(self, tag_id):
        """Remove a tag from this entity"""
        from .tag_models import TagAssociation
        association = TagAssociation.query.filter(
            TagAssociation.tag_id == tag_id,
            TagAssociation.entity_type == self.entity_type,
            TagAssociation.entity_id == self.id
        ).first()

        if association:
            db.session.delete(association)
            return True
        return False
```

### Usage

```python
class Routine(db.Model, TrackableMixin, TaggableMixin):
    __tablename__ = 'routines'

    title = db.Column(db.String(100), nullable=False)
    # ...

    # TaggableMixin provides:
    # - get_tags(), add_tag(), remove_tag()
```

## PolymorphicQueryMixin

### Purpose
Facilitates querying across polymorphic relationships.

### Implementation

```python
class PolymorphicQueryMixin:
    """Mixin with helper methods for polymorphic queries"""

    @classmethod
    def get_entity(cls, entity_type, entity_id):
        """Get an entity by its type and id"""
        model_map = {
            'catchlist_item': 'CatchlistItem',
            'project': 'Project',
            'project_task': 'ProjectTask',
            'routine': 'Routine',
            'session': 'Session',
            'principle': 'Principle'
        }

        if entity_type not in model_map:
            return None

        # Import the appropriate model
        model_name = model_map[entity_type]
        module = __import__('models', fromlist=[model_name])
        model_class = getattr(module, model_name)

        # Query the entity
        return model_class.query.get(entity_id)
```

### Usage

```python
class Comment(db.Model, PolymorphicQueryMixin):
    __tablename__ = 'comments'

    # ...

    @property
    def entity(self):
        """Get the entity this comment belongs to"""
        return self.get_entity(self.entity_type, self.entity_id)
```

## TimeframeMixin

### Purpose
Provides methods for working with date ranges and timeframe hierarchies.

### Implementation

```python
class TimeframeMixin:
    """Mixin for timeframe-related functionality"""

    @property
    def duration_days(self):
        """Calculate duration in days"""
        return (self.end_date - self.start_date).days + 1

    @classmethod
    def get_containing_timeframe(cls, date, timeframe_type, user_id):
        """Get the timeframe of specified type containing the given date"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.type == timeframe_type,
            cls.start_date <= date,
            cls.end_date >= date
        ).first()

    @classmethod
    def create_timeframe_hierarchy(cls, date, user_id):
        """Create or get complete timeframe hierarchy for a date"""
        # Implementation details for creating day/week/month/etc timeframes
        pass
```

### Usage

```python
class Timeframe(db.Model, TimeframeMixin):
    __tablename__ = 'timeframes'

    # ...

    # TimeframeMixin provides:
    # - duration_days property
    # - get_containing_timeframe() class method
    # - create_timeframe_hierarchy() class method
```

## Combining Mixins

Models can use multiple mixins to gain combined functionality:

```python
class Project(db.Model, TrackableMixin, TaggableMixin):
    # Has features from both TrackableMixin and TaggableMixin
    pass
```

## Benefits of Using Mixins

1. **Code Reuse**: Common functionality defined in one place
2. **Consistency**: Uniform behavior across different models
3. **Maintainability**: Changes to shared behavior only need to be made once
4. **Readability**: Clear indication of a model's capabilities through its mixins
5. **Testability**: Mixins can be tested independently
