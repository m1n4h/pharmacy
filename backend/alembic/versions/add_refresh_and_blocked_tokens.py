"""add refresh and blocked tokens

Revision ID: add_refresh_blocked_tokens
Revises: d7f8e9a1b2c3
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_refresh_blocked_tokens'
down_revision = 'd7f8e9a1b2c3'
branch_labels = None
depends_on = None

def upgrade():
    # Create refresh_tokens table
    op.create_table('refresh_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)
    
    # Create blocked_tokens table
    op.create_table('blocked_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('blocked_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blocked_tokens_id'), 'blocked_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_blocked_tokens_token'), 'blocked_tokens', ['token'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_blocked_tokens_token'), table_name='blocked_tokens')
    op.drop_index(op.f('ix_blocked_tokens_id'), table_name='blocked_tokens')
    op.drop_table('blocked_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')