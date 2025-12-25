"""recreate all tables with proper schema

Revision ID: e1234567890a
Revises: d5ee24f6f71c
Create Date: 2025-12-24 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1234567890a'
down_revision: Union[str, Sequence[str], None] = 'd5ee24f6f71c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop personal_access_tokens if it exists with wrong schema
    op.execute('DROP TABLE IF EXISTS "SWORD".personal_access_tokens CASCADE')
    
    # Create users table if it doesn't exist
    op.execute('''
        CREATE TABLE IF NOT EXISTS "SWORD".users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(150) NOT NULL
        )
    ''')
    
    op.execute('CREATE INDEX IF NOT EXISTS ix_SWORD_users_id ON "SWORD".users(id)')
    
    # Create services table if it doesn't exist
    op.execute('''
        CREATE TABLE IF NOT EXISTS "SWORD".services (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    
    op.execute('CREATE INDEX IF NOT EXISTS ix_SWORD_services_id ON "SWORD".services(id)')
    
    # Create personal_access_tokens table
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
    op.create_index('ix_SWORD_personal_access_tokens_user_id', 'personal_access_tokens', ['user_id'], schema='SWORD')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_SWORD_personal_access_tokens_user_id', table_name='personal_access_tokens', schema='SWORD')
    op.drop_table('personal_access_tokens', schema='SWORD')
    op.drop_index('ix_SWORD_services_id', table_name='services', schema='SWORD')
    op.execute('DROP TABLE IF EXISTS "SWORD".services CASCADE')
    op.drop_index('ix_SWORD_users_id', table_name='users', schema='SWORD')
    op.execute('DROP TABLE IF EXISTS "SWORD".users CASCADE')

