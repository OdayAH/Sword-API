"""add status and timestamps to requests

Revision ID: acd617c17063
Revises: 9735174e141d
Create Date: 2026-02-17 11:59:53.553082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acd617c17063'
down_revision: Union[str, Sequence[str], None] = '9735174e141d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # explicitly specify schema for enum
    request_status = sa.Enum('pending', 'approved', 'declined', name='request_status', schema='SWORD')
    request_status.create(op.get_bind(), checkfirst=True)

    # now add columns
    op.add_column(
        'requests',
        sa.Column('status', request_status, nullable=False),
        schema='SWORD'
    )
    op.add_column(
        'requests',
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        schema='SWORD'
    )
    op.add_column(
        'requests',
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema='SWORD'
    )

def downgrade():
    op.drop_column('requests', 'updated_at', schema='SWORD')
    op.drop_column('requests', 'created_at', schema='SWORD')
    op.drop_column('requests', 'status', schema='SWORD')

    request_status = sa.Enum('pending', 'approved', 'declined', name='request_status', schema='SWORD')
    request_status.drop(op.get_bind(), checkfirst=True)