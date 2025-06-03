# Database Migration Guide

## Overview

This application uses Alembic and Flask-Migrate for database schema management. This guide explains the best practices for evolving the database schema while maintaining data integrity.

## Migration Workflow

### 1. Generating Migrations

When you make changes to the database models:

```bash
# Generate a new migration script
flask db migrate -m "Description of changes"

# Review the generated script in migrations/versions/
# Edit if necessary to ensure correct data transformation

# Apply the migration
flask db upgrade
```

### 2. Types of Changes

#### Simple Changes (Auto-generated)

* Adding new tables
* Adding non-nullable columns with defaults
* Adding nullable columns
* Changing column types with compatible conversions
* Adding or removing indexes

#### Complex Changes (Require Manual Editing)

* Adding non-nullable columns to existing tables without defaults
* Renaming columns or tables
* Changing column types with data transformation
* Splitting or merging tables
* Adding or modifying polymorphic relationships

## Best Practices

### 1. Always Review Generated Migrations

Alembic's auto-generated migrations are not always perfect. Always review them for:

* Correct operations (especially for complex changes)
* Potential data loss
* Proper operation ordering

### 2. Make Migrations Reversible

Ensure `downgrade()` functions are properly implemented:

```python
def upgrade():
    # Add a column
    op.add_column('table_name', sa.Column('new_column', sa.String(50)))

def downgrade():
    # Remove the column
    op.drop_column('table_name', 'new_column')
```

### 3. Maintain Data Integrity

When adding non-nullable columns to existing tables:

```python
def upgrade():
    # 1. Add column as nullable
    op.add_column('table_name', sa.Column('new_column', sa.String(50), nullable=True))

    # 2. Update existing rows with a default value
    op.execute("UPDATE table_name SET new_column = 'default value' WHERE new_column IS NULL")

    # 3. Change column to non-nullable
    op.alter_column('table_name', 'new_column', nullable=False)
```

### 4. Use Transactions

Wrap related operations in transactions when appropriate:

```python
def upgrade():
    # Start a transaction for related operations
    connection = op.get_bind()
    transaction = connection.begin()
    try:
        # Multiple operations
        op.add_column('table_name', sa.Column('new_column', sa.String(50)))
        op.execute("UPDATE table_name SET new_column = 'default'")

        # Commit if all successful
        transaction.commit()
    except:
        # Rollback on any error
        transaction.rollback()
        raise
```

### 5. Handling Common Scenarios

#### Renaming Columns

```python
def upgrade():
    # SQLite doesn't support column renames directly
    with op.batch_alter_table('table_name') as batch_op:
        batch_op.alter_column('old_name', new_column_name='new_name')
```

#### Adding Polymorphic Relationships

```python
def upgrade():
    # 1. Add required columns
    op.add_column('table_name', sa.Column('entity_type', sa.String(20), nullable=True))
    op.add_column('table_name', sa.Column('entity_id', sa.Integer, nullable=True))

    # 2. Create index for efficient querying
    op.create_index('idx_entity', 'table_name', ['entity_type', 'entity_id'])

    # 3. If you need to migrate existing data
    op.execute("UPDATE table_name SET entity_type = 'some_type' WHERE entity_type IS NULL")
    op.execute("UPDATE table_name SET entity_id = related_id WHERE entity_id IS NULL")

    # 4. Make columns non-nullable if needed
    op.alter_column('table_name', 'entity_type', nullable=False)
    op.alter_column('table_name', 'entity_id', nullable=False)
```

#### Splitting Tables

```python
def upgrade():
    # 1. Create the new table
    op.create_table(
        'new_table',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('data', sa.String(), nullable=False),
        sa.Column('original_id', sa.Integer(), sa.ForeignKey('original_table.id'))
    )

    # 2. Migrate data
    op.execute("""
        INSERT INTO new_table (data, original_id)
        SELECT json_data->>'specific_field', id FROM original_table
    """)

    # 3. Remove old data if needed
    op.execute("""
        UPDATE original_table
        SET json_data = json_remove(json_data, '$.specific_field')
    """)
```

## Testing Migrations

### 1. Test on a Copy of Production Data

Always test migrations on a copy of production data:

```bash
# Create a testing database from production backup
pg_dump prod_db | psql test_db

# Run migrations on the test database
DATABASE_URL=postgresql://user:pass@localhost/test_db flask db upgrade
```

### 2. Verify Data Integrity

After migration, verify:
- All tables have the expected structure
- Sample data is correctly transformed
- Application functionality works with the new schema

### 3. Test Downgrade Path

Ensure downgrade works correctly:

```bash
# Test downgrading to previous version
flask db downgrade

# Verify database structure is correct after downgrade
# Verify data is preserved properly

# Upgrade again to confirm bidirectional migration works
flask db upgrade
```

## Deployment Considerations

### 1. Database Backup

Always backup the database before applying migrations in production:

```bash
pg_dump production_db > production_backup_$(date +%Y%m%d).sql
```

### 2. Downtime Planning

For major schema changes:
- Schedule maintenance window
- Implement migrations that minimize table locking
- Consider blue/green deployment for zero downtime

### 3. Monitoring

After applying migrations:
- Monitor database performance
- Watch for errors in application logs
- Be prepared to rollback if issues occur

## Common Pitfalls

1. **Adding Non-nullable Columns**: Always add as nullable first, populate data, then change to non-nullable

2. **SQLite Limitations**: SQLite has limited ALTER TABLE support; use batch_alter_table

3. **Large Tables**: Be cautious with migrations on large tables; they can cause long locks

4. **Foreign Keys**: When adding foreign keys, ensure referenced data exists

5. **Missing Downgrade Operations**: Always implement both upgrade and downgrade operations
