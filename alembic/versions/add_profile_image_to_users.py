"""add profile_image to users

Revision ID: b4f2e8c0a1d3
Revises: acd617c17063
Create Date: 2026-03-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b4f2e8c0a1d3'
down_revision: Union[str, Sequence[str], None] = 'acd617c17063'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('profile_image', sa.String(255), nullable=True),
        schema='SWORD',
    )


def downgrade():
    op.drop_column('users', 'profile_image', schema='SWORD')
