# Database Layer

## Overview

The database layer follows a three-tier architecture separating concerns between data structure, data access, and business logic:

- **Models**: Define database schema and ORM mappings (SQLAlchemy)
- **Repositories**: Provide CRUD operations for database access
- **Services**: Implement validation and business logic

**Golden Rule**: API routes should never access repositories directly. Always go through the service layer.

## Directory Structure

    database/
    ├── base/
    │   ├── base_models.py          # Abstract base classes for models
    │   ├── base_repositories.py    # Generic repository implementations
    │   └── exceptions.py           # Custom database exceptions
    ├── config_db.py                # Database configuration and initialization
    ├── db.py                       # SQLAlchemy instance
    ├── users/
    │   ├── user_models.py
    │   ├── user_repository.py
    │   └── user_service.py
    ├── tasks/
    │   ├── task_models.py
    │   ├── task_repository.py
    │   └── task_service.py
    ├── projects/
    │   ├── project_models.py
    │   ├── project_repository.py
    │   └── project_service.py
    └── [other entities...]

**Note**: File naming follows the pattern `{entity}_models.py`, `{entity}_repository.py`, `{entity}_service.py` to avoid confusion when working with multiple entities.

## Core Concepts

### Models

Models define the database schema using SQLAlchemy ORM. All models inherit from one or more base classes that provide common functionality.

#### BaseModel

The foundation for all database models, providing common fields and functionality.

Example:
```
python
from src.database.base.base_models import BaseModel

class SharedResource(BaseModel):
    __tablename__ = "shared_resources"
    name = Column(String, nullable=False)
    # ... additional fields
```
**Provides:**
- Auto-generated `id` (primary key)
- Auto-generated `created_at` and `updated_at` timestamps
- `as_dict(user_timezone)` method for timezone-aware JSON serialization

**Use for**: Shared resources that exist independently of any user (rare in this application).

#### UserOwnedModel

The primary base class for entities belonging to a specific user.

Example:
```
python
from src.database.base.base_models import UserOwnedModel

class Task(UserOwnedModel):
    __tablename__ = "tasks"
    title = Column(String(200), nullable=False)
    # ... additional fields
```
**Provides:**
- Everything from `BaseModel`
- `user_id` foreign key (indexed)
- `user` relationship for accessing the owner
- **Automatic bidirectional relationship** with cascade deletion
- Extended `as_dict()` including `user_id`

**Bidirectional Access:**
- From entity to user: `task.user`
- From user to entities: `user.tasks_list`

**Cascade Deletion:** When a user is deleted, all their owned entities are automatically deleted.

**Use for**: Tasks, Projects, Tags, Principles, and all other user-scoped data.

#### SoftDeleteModel

Extends `BaseModel` with soft delete functionality, allowing records to be marked as deleted without physical removal.

Example:
```
python
from src.database.base.base_models import SoftDeleteModel

class ArchivableEntity(SoftDeleteModel, UserOwnedModel):
    __tablename__ = "archivable_entities"
    # ... fields
```
**Provides:**
- `deleted_at` timestamp field
- `soft_delete()` method to mark as deleted
- `restore()` method to undelete
- `is_deleted` property to check deletion status
- Extended `as_dict()` including `deleted_at`

**Use for**: Entities that need audit trails or recovery capability.

#### Mixins

The codebase includes specialized mixins for cross-cutting concerns:

**TaggableMixin** - Enables polymorphic tag associations:
```
python
class Task(UserOwnedModel, TaggableMixin):
    # Automatically provides:
    # - task.tags relationship
    # - Polymorphic association via tag_associations table
```
**PrincipledMixin** - Enables polymorphic principle associations:
```
python
class Task(UserOwnedModel, PrincipledMixin):
    # Automatically provides:
    # - task.principles relationship
    # - Polymorphic association via principle_associations table
```
These mixins use polymorphic associations to allow tags and principles to be attached to multiple entity types (Tasks, Projects, etc.) without duplicating tables.

#### Timezone-Aware Serialization

All models include timezone-aware `as_dict()` methods that convert UTC timestamps to the user's local timezone:
```
python
def as_dict(self, user_timezone: str = 'UTC') -> Dict[str, Any]:
    data = super().as_dict(user_timezone=user_timezone)
    data.update({
        'title': self.title,
        'completed_at': from_utc(self.completed_at, user_timezone).isoformat() if self.completed_at else None,
        # ... other fields
    })
    return data
```
Always pass the user's timezone when serializing for API responses.

### Repositories

Repositories provide CRUD operations only. No validation, no business logic.

#### BaseRepository[T]

Generic repository for basic database operations.

Example:
```
python
from src.database.base.base_repositories import BaseRepository
from src.database.tags.tag_models import Tag

class TagRepository(BaseRepository[Tag]):
    def __init__(self, session):
        super().__init__(session, Tag)
```
**Provides:**
- `get(id)` - Retrieve by ID
- `list(**filters)` - List all matching filters
- `create(**data)` - Create new record
- `update(instance, **data)` - Update existing record
- `delete(instance)` - Delete record

#### UserOwnedRepository[T]

Repository for user-scoped resources with additional user filtering.

Example:
```
python
from src.database.base.base_repositories import UserOwnedRepository
from src.database.tasks.task_models import Task

class TaskRepository(UserOwnedRepository[Task]):
    def __init__(self, session):
        super().__init__(session, Task)
```
**Provides:**
- Everything from `BaseRepository`
- `get(id, user_id)` - Retrieve by ID and user (enforces ownership)
- `list_for_user(user_id, **filters)` - List all for specific user

#### When to Extend

Most repositories can use the base implementation as-is. Only extend when you need domain-specific queries:
```
python
class TaskRepository(UserOwnedRepository[Task]):
    def __init__(self, session):
        super().__init__(session, Task)
    
    def get_active_tasks_for_project(self, user_id: int, project_id: int):
        """Get all active tasks for a specific project"""
        return self.session.query(self.model_class).filter(
            self.model_class.user_id == user_id,
            self.model_class.project_id == project_id,
            self.model_class.active == True
        ).all()
```
### Services

Services implement validation and business logic. **All external access (API routes) must go through services.**

Example:
```
python
class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo
    
    def create_task(self, user_id: int, data: dict) -> Task:
        # Validate data
        self._validate_title(data.get('title'))
        
        # Ensure user_id is set
        data['user_id'] = user_id
        
        # Use repository for persistence
        return self.repo.create(**data)
    
    def _validate_title(self, title: str):
        if not title or len(title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
```
**Responsibilities:**
- Input validation
- Business rule enforcement
- Data transformation
- Orchestrating multiple repositories (when needed)
- Raising meaningful exceptions

**Not responsible for:**
- Database operations (delegate to repository)
- HTTP concerns (handled by API layer)
- Authentication (handled by API middleware)

## Adding a New Entity

Follow these steps to add a new user-owned entity (e.g., `Note`):

### 1. Create Directory Structure

    database/notes/
    ├── __init__.py
    ├── note_models.py
    ├── note_repository.py
    └── note_service.py

### 2. Define Model

Choose appropriate base class(es) based on requirements:
```
python
# database/notes/note_models.py
from src.database.base.base_models import UserOwnedModel, TaggableMixin
from sqlalchemy import Column, String, Text

class Note(UserOwnedModel, TaggableMixin):
    __tablename__ = "notes"
    
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    
    def as_dict(self, user_timezone: str = 'UTC'):
        data = super().as_dict(user_timezone=user_timezone)
        data.update({
            "title": self.title,
            "content": self.content,
            "tags": [tag.as_dict() for tag in self.tags]
        })
        return data
```
**Automatic relationships:** By inheriting from `UserOwnedModel`, you automatically get:
- `note.user` - access the owning user
- `user.notes_list` - access all notes for a user
- Cascade deletion when user is deleted


### 3. Create Repository

Start with the base implementation:
```
python
# database/notes/note_repository.py
from src.database.base.base_repositories import UserOwnedRepository
from src.database.notes.note_models import Note

class NoteRepository(UserOwnedRepository[Note]):
    def __init__(self, session):
        super().__init__(session, Note)
```
Add custom query methods only if needed for your domain.

### 4. Implement Service

Add validation and business logic:
```
python
# database/notes/note_service.py
from src.database.notes.note_models import Note
from src.database.notes.note_repository import NoteRepository

class NoteService:
    def __init__(self, repo: NoteRepository):
        self.repo = repo
    
    def create_note(self, user_id: int, data: dict) -> Note:
        self._validate_title(data.get("title"))
        data["user_id"] = user_id
        return self.repo.create(**data)
    
    def get_note(self, note_id: int, user_id: int) -> Note:
        note = self.repo.get(note_id, user_id)
        if not note:
            raise ValueError(f"Note {note_id} not found")
        return note
    
    def _validate_title(self, title: str):
        if not title or len(title.strip()) == 0:
            raise ValueError("Note title cannot be empty")
```
### 5. Register in Database Initialization

Import the model in `config_db.py` to ensure tables are created:
```
python
# Add to imports
from src.database.notes.note_models import Note
```

## Common Patterns

### Working with Relationships

**One-to-Many (e.g., Project → Tasks):**

In project_models.py:
```
python
class Project(UserOwnedModel):
    __tablename__ = "projects"
    tasks = relationship("Task", back_populates="project")
```
In task_models.py:
```
python
class Task(UserOwnedModel):
    __tablename__ = "tasks"
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    project = relationship("Project", back_populates="tasks")
```
**Many-to-Many (e.g., Task ↔ Tags, via mixins):**

Uses polymorphic associations through `TaggableMixin` and `PrincipledMixin` - see those mixins in `base/base_models.py` for implementation details.

### Querying with Filters

Repositories support keyword argument filtering:

```python
# Get all completed tasks for a user
completed_tasks = task_repo.list_for_user(user_id=1, completed=True)

# Get all active projects
active_projects = project_repo.list_for_user(user_id=1, active=True)
```



### Handling Soft Deletes

If using `SoftDeleteModel`:

```python
# Soft delete
entity.soft_delete()
session.commit()

# Restore
entity.restore()
session.commit()

# Check status
if entity.is_deleted:
    # Handle deleted entity
```


Remember to filter out soft-deleted records in repository queries when appropriate.

## Database Initialization

### Configuration

Database settings are defined in `database/config_db.py`:
- Database URI (defaults to SQLite in `instance/` directory)
- SQLAlchemy engine configuration
- Session management

### Initialization Flow

1. App factory calls `initialize_database(app)`
2. All tables are created via `db.create_all()`
3. Import all model files to ensure registration


## Architecture Principles

### Layer Separation

    API Layer (routes)
        ↓ (calls)
    Service Layer (business logic)
        ↓ (calls)
    Repository Layer (database access)
        ↓ (uses)
    Model Layer (schema definition)

**Dependency Rule**: Each layer can only depend on layers below it. Never import from a higher layer.

### Ownership and Security

All user-scoped entities use `UserOwnedRepository`, which enforces ownership at the database level:

```python
# This automatically filters by user_id
task = task_repo.get(task_id, user_id)

# Users cannot access other users' data
other_task = task_repo.get(task_id, other_user_id)  # Returns None
```


This prevents data leakage and ensures users can only access their own resources.


## Further Reading

For detailed implementation examples, refer to:
- `tasks/` - Complete user-owned entity with tags and principles
- `projects/` - User-owned entity with one-to-many relationship to tasks
- `tags/` - Polymorphic association implementation
- `base/` - Foundation classes and patterns

The docs directory contains more thorough documentation for the API, database entities, and more.
It's in zim wiki format; only limited pages are duplicated into MD files.

Purpose-focused documentation for database entities can be found in docs/wiki/Design/Entities/
API Route documentation can be found in docs/wiki/API/Routes/