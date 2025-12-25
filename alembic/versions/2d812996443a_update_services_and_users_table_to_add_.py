"""update services and users table to add relation between them

Revision ID: 2d812996443a
Revises: 27ce904a2c4f
Create Date: 2025-12-23 16:40:26.422056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d812996443a'
down_revision: Union[str, Sequence[str], None] = '27ce904a2c4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This migration was incorrectly dropping tables
    # Skipping as tables should be preserved
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
