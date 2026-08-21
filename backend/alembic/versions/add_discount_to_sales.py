"""add discount to sales

Revision ID: add_discount_to_sales
Revises: add_refresh_blocked_tokens
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_discount_to_sales'
down_revision = 'add_refresh_blocked_tokens'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('sales', sa.Column('subtotal', sa.Float(), nullable=False, server_default='0'))
    op.add_column('sales', sa.Column('discount_amount', sa.Float(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('sales', 'discount_amount')
    op.drop_column('sales', 'subtotal')