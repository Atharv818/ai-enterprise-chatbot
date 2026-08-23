"""add data and query_id to messages

Revision ID: b5d7c3d2d8c1
Revises: 68a5eb012b15
Create Date: 2026-08-22 22:04:20.552127

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5d7c3d2d8c1'
down_revision: Union[str, Sequence[str], None] = '68a5eb012b15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('messages', sa.Column('data', sa.Text(), nullable=True))
    op.add_column('messages', sa.Column('query_id', sa.String(length=36), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('messages', 'query_id')
    op.drop_column('messages', 'data')