## Layer Responsibilities

### 1. Models Layer (`models.py`)
- Defines SQLAlchemy models representing database tables
- Contains only schema definitions and basic model methods
- Must include `as_dict()` method for serialization
- No business logic or complex queries
- Includes relationships and foreign keys
- Type hints for all fields

### 2. Repository Layer (`repositories.py`)
- Handles direct database operations (CRUD)
- One repository per feature or group of related models
- Must inherit from BaseRepository for common operations
- No business logic, only database operations
- Returns model instances
- Uses type hints for all methods

### 3. Service Layer (`service.py`)
- Contains all business logic and data validation
- Coordinates between multiple repositories if needed
- Never directly accesses the database (use repository)
- Returns domain objects or model instances
- Handles all error cases
- Implements feature-specific interfaces
- Uses type hints for all methods

## Key Principles

### 1. Dependency Direction
- Services depend on repositories
- Repositories depend on models
- Lower layers must not import from higher layers
- No circular dependencies allowed

### 2. Type Safety
- All methods must include type hints
- Use Optional[] for nullable fields
- Define clear input/output types
- Use dataclasses or Pydantic for data validation

### 3. Error Handling
- Define feature-specific exceptions
- Handle database errors in repository layer
- Handle validation errors in service layer
- Never expose database exceptions to API layer
- Use custom exception classes

### 4. Testing
- Each layer must be independently testable
- Use dependency injection for testing
- Repository tests use test database
- Service tests use mocked repositories
- 100% coverage required for service layer

## Implementation Rules

### DO
- ✅ Keep models simple and focused
- ✅ Use repository pattern for all database access
- ✅ Validate data in service layer
- ✅ Use dependency injection
- ✅ Handle errors explicitly
- ✅ Document public interfaces
- ✅ Write tests for each layer
- ✅ Use type hints consistently

### DON'T
- ❌ Put business logic in models
- ❌ Access database directly from services
- ❌ Mix concerns between layers
- ❌ Use raw SQL (use SQLAlchemy)
- ❌ Handle HTTP concerns in database layer
- ❌ Import from api/ directory
- ❌ Create circular dependencies
- ❌ Skip error handling

## Example Implementation
The `reports/` directory provides a complete reference implementation following these patterns. New features should use this as a template.

## Adding New Features

1. Create new directory under `database/`
2. Create all three required files (models, repositories, service)
3. Define models with all relationships
4. Implement repository extending BaseRepository
5. Create service with complete validation
6. Add tests for all layers
7. Document public interfaces
8. Update database migrations

## Required Patterns

### 1. Model Definition
Every model must include:
- Table name
- Primary key
- Created/updated timestamps
- User ownership (if applicable)
- as_dict() method
- Type hints
- Relationship definitions

### 2. Repository Methods
Every repository must implement:
- get() - Retrieve single item
- list() - Retrieve multiple items
- create() - Create new item
- update() - Update existing item
- delete() - Remove item
- Custom methods as needed

### 3. Service Methods
Every service must implement:
- Data validation
- Error handling
- Business logic
- Repository coordination
- Type-safe interfaces
- Documentation

