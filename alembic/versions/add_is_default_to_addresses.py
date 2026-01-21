"""add is_default to addresses

Revision ID: add_is_default_addresses
Revises: c26dc5fcaeb7
Create Date: 2026-01-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_is_default_addresses'
down_revision: Union[str, Sequence[str], None] = 'c26dc5fcaeb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('addresses', sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.false()), schema='SWORD')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('addresses', 'is_default', schema='SWORD')
