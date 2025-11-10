"""add_api_usage_tracking_table

Revision ID: 35087af8dbee
Revises: bae3f78ee787
Create Date: 2025-09-11 00:16:49.366409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35087af8dbee'
down_revision: Union[str, None] = 'bae3f78ee787'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create API usage tracking table
    op.create_table('api_usage',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('service_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('prompt_cost', sa.Float(), nullable=True),
        sa.Column('completion_cost', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('request_type', sa.String(length=50), nullable=True),
        sa.Column('input_length', sa.Integer(), nullable=True),
        sa.Column('output_length', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_api_usage_user_id', 'api_usage', ['user_id'])
    op.create_index('idx_api_usage_service_type', 'api_usage', ['service_type'])
    op.create_index('idx_api_usage_provider', 'api_usage', ['provider'])
    op.create_index('idx_api_usage_created_at', 'api_usage', ['created_at'])
    
    # Fix vector dimension for user_facts if needed
    # op.alter_column('user_facts', 'embedding',
    #            existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
    #            type_=pgvector.sqlalchemy.vector.VECTOR(dim=384),
    #            existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_api_usage_created_at', 'api_usage')
    op.drop_index('idx_api_usage_provider', 'api_usage')
    op.drop_index('idx_api_usage_service_type', 'api_usage')
    op.drop_index('idx_api_usage_user_id', 'api_usage')
    
    # Drop API usage table
    op.drop_table('api_usage')
    
    # Revert vector dimension if needed
    # op.alter_column('user_facts', 'embedding',
    #            existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=384),
    #            type_=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
    #            existing_nullable=True)
