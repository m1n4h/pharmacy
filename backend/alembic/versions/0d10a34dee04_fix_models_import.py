"""fix models import

Revision ID: 0d10a34dee04
Revises: f6eb623a5544
Create Date: 2025-11-16 12:32:35.698095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d10a34dee04'
down_revision: Union[str, Sequence[str], None] = 'f6eb623a5544'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
