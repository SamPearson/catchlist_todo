# Data Model Architecture

## Core Concepts

The application's data model revolves around these key concepts:

1. **Trackable Entities**: Tasks and task-like items that can be monitored, assigned, and completed
2. **Time-Based Scheduling**: Routines that generate concrete time-bound sessions
3. **Commitment System**: Connecting tasks to specific timeframes for accountability
4. **Reporting Framework**: Hierarchical timeframes for structured reflection
5. **Progress Tracking**: Check-ins and comments to monitor advancement

## Model Hierarchy

### 1. User Management

#### User
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - owned entities
    catchlist_items = db.relationship('CatchlistItem', backref='user', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
    routines = db.relationship('Routine', backref='user', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', backref='user', lazy=True, cascade='all, delete-orphan')
    principles = db.relationship('Principle', backref='user', lazy=True, cascade='all, delete-orphan')
    timeframes = db.relationship('Timeframe', backref='user', lazy=True, cascade='all, delete-orphan')
```

#### BlacklistedToken
```python
class BlacklistedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
```

### 2. Task Models

#### Trackable Interface (Mixin)
```python
class TrackableMixin:
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

    # Polymorphic relationships
    comments = db.relationship('Comment', 
                              primaryjoin='and_(Comment.entity_type==\"<entity_type>\", '
                                         'Comment.entity_id==<entity_class>.id)',
                              lazy=True)

    check_ins = db.relationship('Checkin',
                               primaryjoin='and_(Checkin.entity_type==\"<entity_type>\", '
                                          'Checkin.entity_id==<entity_class>.id)',
                               lazy=True)
```

#### CatchlistItem
```python
class CatchlistItem(db.Model, TrackableMixin):
    __tablename__ = 'catchlist_items'

    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # active/archived/someday

    # Relationships
    commitments = db.relationship('Commitment',
                                primaryjoin='and_(Commitment.entity_type=="catchlist_item", '
                                           'Commitment.entity_id==CatchlistItem.id)',
                                lazy=True)

    tags = db.relationship('Tag', secondary='tag_associations',
                         primaryjoin='and_(TagAssociation.entity_type=="catchlist_item", '
                                    'TagAssociation.entity_id==CatchlistItem.id)',
                         secondaryjoin='TagAssociation.tag_id==Tag.id',
                         lazy='joined')
```

#### Project
```python
class Project(db.Model, TrackableMixin):
    __tablename__ = 'projects'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active', nullable=False)  # active/completed/archived
    principle_id = db.Column(db.Integer, db.ForeignKey('principles.id'), nullable=True)

    # Relationships
    tasks = db.relationship('ProjectTask', backref='project', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='tag_associations',
                         primaryjoin='and_(TagAssociation.entity_type=="project", '
                                    'TagAssociation.entity_id==Project.id)',
                         secondaryjoin='TagAssociation.tag_id==Tag.id',
                         lazy='joined')
```

#### ProjectTask
```python
class ProjectTask(db.Model, TrackableMixin):
    __tablename__ = 'project_tasks'

    content = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/completed

    # Relationships
    commitments = db.relationship('Commitment',
                                primaryjoin='and_(Commitment.entity_type=="project_task", '
                                           'Commitment.entity_id==ProjectTask.id)',
                                lazy=True)
```

### 3. Time Management Models

#### Routine
```python
class Routine(db.Model, TrackableMixin):
    __tablename__ = 'routines'

    title = db.Column(db.String(100), nullable=False)
    schedule = db.Column(db.Text, nullable=False)  # RRULE format
    duration = db.Column(db.Interval, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)  # active/paused/archived

    # Relationships
    sessions = db.relationship('Session', backref='routine', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='tag_associations',
                         primaryjoin='and_(TagAssociation.entity_type=="routine", '
                                    'TagAssociation.entity_id==Routine.id)',
                         secondaryjoin='TagAssociation.tag_id==Tag.id',
                         lazy='joined')
```

#### Session
```python
class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routines.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled/completed/cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    commitments = db.relationship('Commitment',
                                primaryjoin='and_(Commitment.entity_type=="session", '
                                           'Commitment.entity_id==Session.id)',
                                lazy=True)
```

#### Commitment
```python
class Commitment(db.Model):
    __tablename__ = 'commitments'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(20), nullable=False)  # catchlist_item/project_task/session
    entity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    time_box = db.Column(db.Interval)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index for polymorphic relationship
    __table_args__ = (
        db.Index('idx_commitment_entity', 'entity_type', 'entity_id'),
    )
```

### 4. Progress Tracking Models

#### Checkin
```python
class Checkin(db.Model):
    __tablename__ = 'checkins'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(20), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.Text)
    metrics = db.Column(db.JSON)

    # Composite index for polymorphic relationship
    __table_args__ = (
        db.Index('idx_checkin_entity', 'entity_type', 'entity_id'),
    )
```

#### Comment
```python
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(20), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite index for polymorphic relationship
    __table_args__ = (
        db.Index('idx_comment_entity', 'entity_type', 'entity_id'),
    )
```

### 5. Reporting Models

#### Timeframe
```python
class Timeframe(db.Model):
    __tablename__ = 'timeframes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # day/week/month/season/year
    parent_id = db.Column(db.Integer, db.ForeignKey('timeframes.id'), nullable=True)

    # Relationships
    report = db.relationship('Report', backref='timeframe', uselist=False, lazy=True, cascade='all, delete-orphan')
    sub_timeframes = db.relationship('Timeframe', backref=db.backref('parent', remote_side=[id]), lazy=True)

    # Indexes
    __table_args__ = (
        db.Index('idx_timeframe_date_range', 'user_id', 'start_date', 'end_date'),
    )
```

#### Report
```python
class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    timeframe_id = db.Column(db.Integer, db.ForeignKey('timeframes.id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    metadata = db.Column(db.JSON)  # For sleep, mood, food, gratitude, etc.
    notes = db.Column(db.Text)
    metrics = db.Column(db.JSON)  # For calculated/aggregated metrics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Query property to get associated commitments
    @property
    def commitments(self):
        """Get all commitments within this report's timeframe"""
        from .commitment_models import Commitment
        return Commitment.query.filter(
            Commitment.user_id == self.user_id,
            Commitment.due_date >= self.timeframe.start_date,
            Commitment.due_date <= self.timeframe.end_date
        ).all()
```

### 6. Supporting Models

#### Tag
```python
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#000000')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint per user
    __table_args__ = (
        db.UniqueConstraint('name', 'user_id', name='uix_tag_name_user'),
    )
```

#### TagAssociation
```python
class TagAssociation(db.Model):
    __tablename__ = 'tag_associations'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    entity_type = db.Column(db.String(20), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)

    # Composite index and unique constraint
    __table_args__ = (
        db.Index('idx_tag_association_entity', 'entity_type', 'entity_id'),
        db.UniqueConstraint('tag_id', 'entity_type', 'entity_id', name='uix_tag_entity'),
    )
```

#### Principle
```python
class Principle(db.Model):
    __tablename__ = 'principles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)  # active/archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = db.relationship('Project', backref='principle', lazy=True)

    # Unique constraint per user
    __table_args__ = (
        db.UniqueConstraint('title', 'user_id', name='uix_principle_title_user'),
    )
```

## Key Relationships

### 1. Polymorphic Relationships

The system uses entity_type/entity_id pattern to implement polymorphic relationships:

```
Commitment ──┬── CatchlistItem
              ├── ProjectTask
              └── Session

Checkin ─────┬── CatchlistItem
              ├── Project
              ├── ProjectTask
              ├── Routine
              └── Principle

Comment ─────┬── CatchlistItem
              ├── Project
              ├── ProjectTask
              ├── Routine
              └── Principle

TagAssoc ────┬── CatchlistItem
              ├── Project
              ├── ProjectTask
              └── Routine
```

### 2. Hierarchical Relationships

```
User
 ├── Projects
 │    └── ProjectTasks
 ├── CatchlistItems
 ├── Routines
 │    └── Sessions
 ├── Principles
 │    └── Projects
 └── Timeframes
      ├── Sub-Timeframes
      └── Reports
```

### 3. Commitment Flow

```
Trackable Entity ───► Commitment ───► Timeframe ◄──── Report
       │                                   ▲
       │                                   │
       ▼                                   │
     Checkins                         Sub-Timeframes
```

## Implementation Notes

### 1. Status Transitions

Entities should have well-defined status transitions:

- **CatchlistItem**: active ↔ archived ↔ someday
- **Project**: active → completed → archived
- **ProjectTask**: pending → completed
- **Routine**: active ↔ paused → archived
- **Session**: scheduled → completed/cancelled
- **Commitment**: pending → completed

### 2. Cascading Operations

- Deleting a User cascades to all owned entities
- Deleting a Project cascades to all ProjectTasks
- Deleting a Routine cascades to all Sessions
- Deleting a Timeframe cascades to its Report and affects child Timeframes

### 3. Entity Type Values

Consistent entity_type values across the system:

- "catchlist_item"
- "project"
- "project_task"
- "routine"
- "session"
- "principle"

### 4. Database Indexes

Critical indexes for performance:

- Polymorphic relationships (entity_type + entity_id)
- Date ranges for timeframes and commitments
- User ownership across all entities
- Unique constraints for user-specific items

## Future Extensions

1. **Enhanced Tagging System**
   - Tag hierarchies
   - Auto-tagging based on content
   - Tag statistics and insights

2. **Activity Stream**
   - Unified timeline of all system activities
   - Filtering and search capabilities

3. **Integration Points**
   - Calendar sync extensions
   - Third-party task system imports
   - Export capabilities

4. **Extended Metrics**
   - Time tracking integration
   - Predictive analytics
   - Completion rate forecasting
