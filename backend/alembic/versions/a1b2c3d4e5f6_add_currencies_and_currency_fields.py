"""add currencies and currency fields

Revision ID: a1b2c3d4e5f6
Revises: 5fe7ceabd624
Create Date: 2026-08-20 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5fe7ceabd624'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('currencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('rate_to_tzs', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_currencies_code'), 'currencies', ['code'], unique=True)
    op.create_index(op.f('ix_currencies_id'), 'currencies', ['id'], unique=False)

    # Seed default currencies
    op.bulk_insert(
        sa.table(
            'currencies',
            sa.column('id', sa.Integer()),
            sa.column('code', sa.String(3)),
            sa.column('name', sa.String()),
            sa.column('symbol', sa.String()),
            sa.column('rate_to_tzs', sa.Float()),
        ),
        [
            {'id': 1, 'code': 'TZS', 'name': 'Tanzanian Shilling', 'symbol': 'TSh', 'rate_to_tzs': 1.0},
            {'id': 2, 'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'rate_to_tzs': 2650.0},
            {'id': 3, 'code': 'ZMW', 'name': 'Zambian Kwacha', 'symbol': 'K', 'rate_to_tzs': 105.0},
            {'id': 4, 'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'rate_to_tzs': 2900.0},
            {'id': 5, 'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'rate_to_tzs': 3400.0},
            {'id': 6, 'code': 'KES', 'name': 'Kenyan Shilling', 'symbol': 'KSh', 'rate_to_tzs': 20.5},
        ],
    )

    # Settings: add default_currency
    op.add_column('settings', sa.Column('default_currency', sa.String(length=3), nullable=True))

    # Purchases: add currency fields
    op.add_column('purchases', sa.Column('currency_code', sa.String(length=3), nullable=True))
    op.add_column('purchases', sa.Column('currency_amount', sa.Float(), nullable=True))
    op.add_column('purchases', sa.Column('currency_rate', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('purchases', 'currency_rate')
    op.drop_column('purchases', 'currency_amount')
    op.drop_column('purchases', 'currency_code')
    op.drop_column('settings', 'default_currency')
    op.drop_index(op.f('ix_currencies_id'), table_name='currencies')
    op.drop_index(op.f('ix_currencies_code'), table_name='currencies')
    op.drop_table('currencies')