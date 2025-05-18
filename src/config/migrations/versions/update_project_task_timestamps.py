"""update project task timestamps

Revision ID: update_project_task_timestamps
Revises: drop_legacy_tables
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'update_project_task_timestamps'
down_revision = 'drop_legacy_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Update created_at and updated_at columns to use database-level defaults
    op.alter_column('project_task', 'created_at',
                    server_default=func.now(),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)
    
    op.alter_column('project_task', 'updated_at',
                    server_default=func.now(),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)

def downgrade():
    # Revert to Python-level defaults
    op.alter_column('project_task', 'created_at',
                    server_default=None,
                    existing_type=sa.DateTime(),
                    existing_nullable=False)
    
    op.alter_column('project_task', 'updated_at',
                    server_default=None,
                    existing_type=sa.DateTime(),
                    existing_nullable=False) 