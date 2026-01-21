"""add role_id foreign key to users table

Revision ID: add_role_id_to_users
Revises: remove_description_from_roles
Create Date: 2026-01-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_role_id_to_users'
down_revision = 'remove_description_from_roles'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('role_id', sa.Integer(), nullable=False, server_default='1'),
        schema='SWORD'
    )
    op.create_foreign_key(
        'fk_users_role_id',
        'users',
        'roles',
        ['role_id'],
        ['id'],
        source_schema='SWORD',
        referent_schema='SWORD'
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_role_id', 'users', schema='SWORD')
    op.drop_column('users', 'role_id', schema='SWORD')
