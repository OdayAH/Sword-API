"""rename refresh_tokens to personal_access_tokens

Revision ID: 06f6f80e863d
Revises: 2d812996443a
Create Date: 2025-12-23 17:17:40.544229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06f6f80e863d'
down_revision: Union[str, Sequence[str], None] = '2d812996443a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
