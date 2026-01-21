"""remove description column from roles table

Revision ID: remove_description_from_roles
Revises: add_roles_table_with_defaults
Create Date: 2026-01-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_description_from_roles'
down_revision = 'add_roles_table_with_defaults'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('roles', 'description', schema='SWORD')


def downgrade() -> None:
    op.add_column('roles', sa.Column('description', sa.String(255), nullable=True), schema='SWORD')
