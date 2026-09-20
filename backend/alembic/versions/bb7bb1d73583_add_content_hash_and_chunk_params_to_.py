"""add content_hash and chunk_params to documents

Revision ID: bb7bb1d73583
Revises: b5d7c3d2d8c1
Create Date: 2026-08-29 03:30:08.183519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb7bb1d73583'
down_revision: Union[str, Sequence[str], None] = 'b5d7c3d2d8c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("documents", sa.Column("content_hash", sa.String(length=64), nullable=True))
    op.add_column("documents", sa.Column("chunk_params", sa.String(length=32), nullable=True))
    op.create_index(
        "ix_documents_tenant_content_hash",
        "documents",
        ["tenant_id", "content_hash"],
    )


def downgrade() -> None:
    op.drop_index("ix_documents_tenant_content_hash", table_name="documents")
    op.drop_column("documents", "chunk_params")
    op.drop_column("documents", "content_hash")
