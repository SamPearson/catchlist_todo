# Data Access Patterns

## Overview

This document outlines recommended patterns for accessing and manipulating data across the application. Following these patterns ensures consistency, performance, and maintainability.

## Entity Access Patterns

### Direct Entity Access

#### Get Single Entity

```python
def get_catchlist_item(item_id, user_id):
    """Get a single catchlist item, ensuring it belongs to the user"""
    return CatchlistItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
```

#### Get Multiple Entities

```python
def get_all_projects(user_id, status=None):
    """Get all projects for a user, optionally filtered by status"""
    query = Project.query.filter_by(user_id=user_id)

    if status:
        query = query.filter_by(status=status)

    return query.order_by(Project.created_at.desc()).all()
```

### Polymorphic Entity Access

#### Get Entity by Type and ID

```python
def get_entity(entity_type, entity_id, user_id):
    """Get an entity of any type by its type string and ID"""
    model_map = {
        'catchlist_item': CatchlistItem,
        'project': Project,
        'project_task': ProjectTask,
        'routine': Routine,
        'session': Session,
        'principle': Principle
    }

    if entity_type not in model_map:
        raise ValueError(f"Unknown entity type: {entity_type}")

    model_class = model_map[entity_type]
    entity = model_class.query.filter_by(id=entity_id)

    # Add user_id filter if the model has user_id (most do except Session)
    if hasattr(model_class, 'user_id'):
        entity = entity.filter_by(user_id=user_id)

    return entity.first_or_404()
```

### Relationship Access

#### Access Related Entities

```python
def get_project_tasks(project_id, user_id):
    """Get all tasks for a project, ensuring the project belongs to the user"""
    project = Project.query.filter_by(id=project_id, user_id=user_id).first_or_404()
    return ProjectTask.query.filter_by(project_id=project.id).order_by(ProjectTask.order).all()
```

#### Access Polymorphic Relationships

```python
def get_entity_comments(entity_type, entity_id, user_id):
    """Get comments for any entity type"""
    # First verify the entity exists and belongs to the user
    entity = get_entity(entity_type, entity_id, user_id)

    # Then get its comments
    return Comment.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(Comment.timestamp.desc()).all()
```

## Time-Based Access Patterns

### Get Entities by Date Range

```python
def get_commitments_by_date_range(user_id, start_date, end_date):
    """Get all commitments within a date range"""
    return Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.due_date >= start_date,
        Commitment.due_date <= end_date
    ).order_by(Commitment.due_date).all()
```

### Get Current Timeframe

```python
def get_current_timeframe(user_id, timeframe_type, date=None):
    """Get the current timeframe of specified type containing the given date"""
    if date is None:
        date = datetime.now().date()

    return Timeframe.query.filter(
        Timeframe.user_id == user_id,
        Timeframe.type == timeframe_type,
        Timeframe.start_date <= date,
        Timeframe.end_date >= date
    ).first()
```

## Complex Query Patterns

### Aggregate Data for Reports

```python
def get_report_statistics(timeframe_id, user_id):
    """Get statistics for a report"""
    # Get the timeframe
    timeframe = Timeframe.query.filter_by(id=timeframe_id, user_id=user_id).first_or_404()

    # Get all commitments within the timeframe
    commitments = Commitment.query.filter(
        Commitment.user_id == user_id,
        Commitment.due_date >= timeframe.start_date,
        Commitment.due_date <= timeframe.end_date
    ).all()

    # Calculate statistics
    total = len(commitments)
    completed = sum(1 for c in commitments if c.completed)
    completion_rate = completed / total if total > 0 else 0

    # Get tag distribution
    tag_stats = {}
    for commitment in commitments:
        entity = get_entity(commitment.entity_type, commitment.entity_id, user_id)
        if hasattr(entity, 'tags'):
            for tag in entity.tags:
                if tag.id not in tag_stats:
                    tag_stats[tag.id] = {'tag': tag, 'count': 0, 'completed': 0}
                tag_stats[tag.id]['count'] += 1
                if commitment.completed:
                    tag_stats[tag.id]['completed'] += 1

    return {
        'total': total,
        'completed': completed,
        'completion_rate': completion_rate,
        'tags': list(tag_stats.values())
    }
```

### Filter by Tags

```python
def get_entities_by_tag(user_id, tag_id, entity_types=None):
    """Get entities with a specific tag"""
    # Base query for tag associations
    query = db.session.query(TagAssociation).filter(
        TagAssociation.tag_id == tag_id
    )

    # Filter by entity types if specified
    if entity_types:
        query = query.filter(TagAssociation.entity_type.in_(entity_types))

    # Get the associations
    associations = query.all()

    # Group by entity type for efficient fetching
    grouped = {}
    for assoc in associations:
        if assoc.entity_type not in grouped:
            grouped[assoc.entity_type] = []
        grouped[assoc.entity_type].append(assoc.entity_id)

    # Fetch entities by type
    results = []
    for entity_type, ids in grouped.items():
        model_class = get_model_class(entity_type)
        entities = model_class.query.filter(
            model_class.id.in_(ids),
            model_class.user_id == user_id
        ).all()
        results.extend(entities)

    return results
```

## Data Modification Patterns

### Creating Entities

```python
def create_project(user_id, data):
    """Create a new project"""
    project = Project(
        user_id=user_id,
        title=data['title'],
        description=data.get('description', ''),
        due_date=data.get('due_date'),
        status='active'
    )

    db.session.add(project)

    # Create tasks if provided
    if 'tasks' in data:
        for i, task_data in enumerate(data['tasks']):
            task = ProjectTask(
                project_id=project.id,
                user_id=user_id,
                content=task_data['content'],
                order=i,
                status='pending'
            )
            db.session.add(task)

    # Add tags if provided
    if 'tag_ids' in data:
        for tag_id in data['tag_ids']:
            # Verify tag belongs to user
            tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
            if tag:
                project.add_tag(tag.id)

    db.session.commit()
    return project
```

### Updating Entities

```python
def update_catchlist_item(item_id, user_id, data):
    """Update a catchlist item"""
    item = CatchlistItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()

    # Update basic fields
    if 'content' in data:
        item.content = data['content']
    if 'status' in data:
        item.status = data['status']

    # Update tags
    if 'tag_ids' in data:
        # Clear existing tags
        for tag in item.get_tags():
            item.remove_tag(tag.id)

        # Add new tags
        for tag_id in data['tag_ids']:
            tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
            if tag:
                item.add_tag(tag.id)

    db.session.commit()
    return item
```

## Scheduled Task Patterns

### Generate Sessions from Routines

```python
def generate_sessions_for_date_range(start_date, end_date, user_id=None):
    """Generate sessions for all routines in a date range"""
    from dateutil.rrule import rrulestr
    from dateutil.parser import parse
    import pytz

    # Get active routines
    query = Routine.query.filter_by(status='active')
    if user_id:
        query = query.filter_by(user_id=user_id)

    routines = query.all()
    created_sessions = []

    # Convert dates to datetime for rrule processing
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Process each routine
    for routine in routines:
        # Parse the RRULE
        rule = rrulestr(routine.schedule, dtstart=start_datetime)

        # Get occurrences in the date range
        occurrences = rule.between(start_datetime, end_datetime, inc=True)

        for occurrence in occurrences:
            # Check if session already exists
            existing = Session.query.filter_by(
                routine_id=routine.id,
                start_time=occurrence
            ).first()

            if not existing:
                # Calculate end time based on duration
                end_time = occurrence + routine.duration

                # Create new session
                session = Session(
                    routine_id=routine.id,
                    start_time=occurrence,
                    end_time=end_time,
                    status='scheduled'
                )
                db.session.add(session)
                created_sessions.append(session)

                # Create associated commitment
                commitment = Commitment(
                    entity_type='session',
                    entity_id=session.id,
                    user_id=routine.user_id,
                    due_date=occurrence.date(),
                    time_box=routine.duration
                )
                db.session.add(commitment)

    db.session.commit()
    return created_sessions
```

## Transaction Patterns

### Atomic Operations

```python
def move_task_between_projects(task_id, target_project_id, user_id):
    """Move a task from one project to another"""
    task = ProjectTask.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    target_project = Project.query.filter_by(id=target_project_id, user_id=user_id).first_or_404()

    # Start a transaction
    try:
        # Update task order in source project
        source_tasks = ProjectTask.query.filter(
            ProjectTask.project_id == task.project_id,
            ProjectTask.id != task.id,
            ProjectTask.order > task.order
        ).all()

        for t in source_tasks:
            t.order -= 1

        # Update task project and order
        task.project_id = target_project.id
        task.order = db.session.query(db.func.max(ProjectTask.order)).filter(
            ProjectTask.project_id == target_project.id
        ).scalar() or 0
        task.order += 1

        db.session.commit()
        return task
    except Exception as e:
        db.session.rollback()
        raise e
```

## Best Practices

### 1. Use Query Filtering

Always filter queries by user_id when possible for security:

```python
# Good
Project.query.filter_by(user_id=user_id).all()

# Avoid
Project.query.all()  # Potential security issue
```

### 2. Handle Polymorphic Relationships Carefully

When working with entity_type/entity_id patterns:

```python
# Always validate entity type
valid_types = ['catchlist_item', 'project_task', 'session']
if entity_type not in valid_types:
    raise ValueError(f"Invalid entity type: {entity_type}")

# Always verify entity exists and belongs to user
entity = get_entity(entity_type, entity_id, user_id)
if not entity:
    raise ValueError(f"Entity not found: {entity_type} {entity_id}")
```

### 3. Optimize Queries for N+1 Problems

Use eager loading for related entities:

```python
# Poor performance (N+1 problem)
projects = Project.query.filter_by(user_id=user_id).all()
for project in projects:
    tasks = project.tasks  # Each project causes a separate query

# Better performance
projects = Project.query.options(
    db.joinedload(Project.tasks)
).filter_by(user_id=user_id).all()
```

### 4. Use Transactions for Multi-Step Operations

```python
try:
    # Multiple database operations
    db.session.add(entity1)
    db.session.add(entity2)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    raise e
```

### 5. Implement Custom Query Methods on Models

```python
class Project(db.Model, TrackableMixin):
    # ... model fields

    @classmethod
    def get_active_projects_with_tasks(cls, user_id):
        """Get all active projects with their tasks"""
        return cls.query.options(
            db.joinedload(cls.tasks)
        ).filter_by(
            user_id=user_id,
            status='active'
        ).order_by(cls.title).all()
```

### 6. Use Bulk Operations for Performance

```python
def bulk_update_task_status(task_ids, status, user_id):
    """Update multiple tasks at once"""
    # Verify all tasks belong to user
    task_count = ProjectTask.query.filter(
        ProjectTask.id.in_(task_ids),
        ProjectTask.user_id == user_id
    ).count()

    if task_count != len(task_ids):
        raise ValueError("Some tasks do not belong to the user")

    # Bulk update
    ProjectTask.query.filter(ProjectTask.id.in_(task_ids)).update(
        {ProjectTask.status: status},
        synchronize_session=False
    )

    db.session.commit()
```
