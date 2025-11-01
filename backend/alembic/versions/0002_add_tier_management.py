"""Add tier management fields to users table

Revision ID: 0002
Revises: 0001
Create Date: 2025-11-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    """Add tier management columns to users table."""
    # Add tier management fields
    op.add_column('users', sa.Column('tier', sa.String(), nullable=False, server_default='free'))
    op.add_column('users', sa.Column('ai_analyses_used', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('ai_analyses_limit', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('users', sa.Column('trial_exhausted_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add game statistics fields
    op.add_column('users', sa.Column('total_games', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('analyzed_games', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    """Remove tier management columns from users table."""
    op.drop_column('users', 'analyzed_games')
    op.drop_column('users', 'total_games')
    op.drop_column('users', 'trial_exhausted_at')
    op.drop_column('users', 'ai_analyses_limit')
    op.drop_column('users', 'ai_analyses_used')
    op.drop_column('users', 'tier')
