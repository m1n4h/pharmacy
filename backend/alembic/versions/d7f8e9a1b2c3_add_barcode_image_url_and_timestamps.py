"""add barcode image_url and timestamps

Revision ID: d7f8e9a1b2c3
Revises: c6fe0d05f026
Create Date: 2025-01-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7f8e9a1b2c3'
down_revision: Union[str, Sequence[str], None] = 'c6fe0d05f026'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add barcode and image_url to medicines table
    op.add_column('medicines', sa.Column('barcode', sa.String(), nullable=True))
    op.add_column('medicines', sa.Column('image_url', sa.String(), nullable=True))
    
    # Add created_at to sales table
    op.add_column('sales', sa.Column('created_at', sa.DateTime(), nullable=True))
    
    # Add created_at to purchases table
    op.add_column('purchases', sa.Column('created_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns in reverse order
    op.drop_column('purchases', 'created_at')
    op.drop_column('sales', 'created_at')
    op.drop_column('medicines', 'image_url')
    op.drop_column('medicines', 'barcode')