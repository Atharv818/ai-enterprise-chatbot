"""add multi-tenancy
Revision ID: 21c83f063a6f
Revises: aefb2dfb785e
Create Date: 2026-08-07 02:03:36.869347
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision: str = '21c83f063a6f'
down_revision: Union[str, Sequence[str], None] = 'aefb2dfb785e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the tenants table
    op.create_table('tenants',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    # 2. Insert a default tenant for all existing data to belong to
    default_tenant_id = "00000000-0000-0000-0000-000000000001"
    op.execute(
        f"INSERT INTO tenants (id, name, created_at) "
        f"VALUES ('{default_tenant_id}', 'Default Tenant', now())"
    )

    # 3. Add tenant_id columns as NULLABLE first (so existing rows don't break)
    op.add_column('conversations', sa.Column('tenant_id', sa.String(length=36), nullable=True))
    op.add_column('documents', sa.Column('tenant_id', sa.String(length=36), nullable=True))
    op.add_column('ingested_tables', sa.Column('tenant_id', sa.String(length=36), nullable=True))

    # 4. Backfill every existing row with the default tenant
    op.execute(f"UPDATE conversations SET tenant_id = '{default_tenant_id}' WHERE tenant_id IS NULL")
    op.execute(f"UPDATE documents SET tenant_id = '{default_tenant_id}' WHERE tenant_id IS NULL")
    op.execute(f"UPDATE ingested_tables SET tenant_id = '{default_tenant_id}' WHERE tenant_id IS NULL")

    # 5. Now that every row has a value, make the column required
    op.alter_column('conversations', 'tenant_id', nullable=False)
    op.alter_column('documents', 'tenant_id', nullable=False)
    op.alter_column('ingested_tables', 'tenant_id', nullable=False)

    # 6. Add the foreign key constraints
    op.create_foreign_key(None, 'conversations', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key(None, 'documents', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key(None, 'ingested_tables', 'tenants', ['tenant_id'], ['id'])

    # NOTE: doc_{uuid} tables are intentionally NOT touched here.
    # They are dynamically created outside SQLAlchemy's tracked models
    # and must never be dropped by a migration.


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'ingested_tables', type_='foreignkey')
    op.drop_column('ingested_tables', 'tenant_id')
    op.drop_constraint(None, 'documents', type_='foreignkey')
    op.drop_column('documents', 'tenant_id')
    op.drop_constraint(None, 'conversations', type_='foreignkey')
    op.drop_column('conversations', 'tenant_id')
    op.drop_table('tenants')

    