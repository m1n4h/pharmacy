"""create users table

Revision ID: f6eb623a5544
Revises: e2494f176cbc
Create Date: 2025-11-16 12:16:16.252248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6eb623a5544'
down_revision: Union[str, Sequence[str], None] = 'e2494f176cbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
