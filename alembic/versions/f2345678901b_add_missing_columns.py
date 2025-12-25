"""fix personal_access_tokens table schema

Revision ID: f2345678901b
Revises: e1234567890a
Create Date: 2025-12-24 13:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2345678901b'
down_revision: Union[str, Sequence[str], None] = 'e1234567890a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the personal_access_tokens table if it exists with wrong schema
    op.execute('DROP TABLE IF EXISTS "SWORD".personal_access_tokens CASCADE')
    
    # Recreate with correct schema
    op.create_table('personal_access_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(length=1024), nullable=False),
    sa.Column('refresh_token', sa.String(length=1024), nullable=False),
    sa.Column('access_expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('refresh_expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['SWORD.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('access_token'),
    sa.UniqueConstraint('refresh_token'),
    schema='SWORD'
    )
    op.create_index('ix_SWORD_personal_access_tokens_user_id', 'personal_access_tokens', ['user_id'], unique=False, schema='SWORD')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_SWORD_personal_access_tokens_user_id', table_name='personal_access_tokens', schema='SWORD')
    op.drop_table('personal_access_tokens', schema='SWORD')
