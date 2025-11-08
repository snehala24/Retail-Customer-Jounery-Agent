"""initial schema (products + inventory + customers + orders + loyalty)

Revision ID: 32a2961b8193
Revises:
Create Date: 2025-11-06 18:49:31.717395
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '32a2961b8193'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - keep existing products, add new tables."""

    # ✅ DO NOT DROP PRODUCTS TABLE (already exists)
    # Create new tables only if they don't exist

    op.create_table(
        'inventory',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('product_id', sa.Integer, nullable=False),
        sa.Column('quantity', sa.Integer, default=0),
        sa.Column('location', sa.String(100)),
    )

    op.create_table(
        'customers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('customer_id', sa.String(50), unique=True),
        sa.Column('name', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
    )

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_id', sa.String(50), unique=True),
        sa.Column('customer_id', sa.String(50)),
        sa.Column('product_id', sa.Integer),
        sa.Column('quantity', sa.Integer),
        sa.Column('total_price', sa.Float),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'loyalty',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('customer_id', sa.String(50)),
        sa.Column('points', sa.Integer, default=0),
        sa.Column('tier', sa.String(50), default='Bronze'),
    )


def downgrade() -> None:
    """Downgrade schema - remove newly added tables."""

    op.drop_table('loyalty')
    op.drop_table('orders')
    op.drop_table('customers')
    op.drop_table('inventory')
