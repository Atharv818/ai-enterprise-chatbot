"""create conversations and messages tables
Revision ID: aefb2dfb785e
Revises: 2abb46396f4a
Create Date: 2026-08-05 01:31:14.733658
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision: str = 'aefb2dfb785e'
down_revision: Union[str, Sequence[str], None] = '2abb46396f4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('conversations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('conversation_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('route', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('messages')
    op.drop_table('conversations')
    