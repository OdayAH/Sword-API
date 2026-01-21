"""add roles table with default user and provider roles

Revision ID: add_roles_table_with_defaults
Revises: add_is_default_addresses
Create Date: 2026-01-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_roles_table_with_defaults'
down_revision = 'add_is_default_addresses'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='SWORD'
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], schema='SWORD')
    
    # Insert default roles
    op.execute(
        sa.insert(sa.table(
            'roles',
            sa.column('name'),
            sa.column('description'),
            schema='SWORD'
        )).values([
            {'name': 'user'},
            {'name': 'provider'},
        ])
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_roles_id'), table_name='roles', schema='SWORD')
    op.drop_table('roles', schema='SWORD')
