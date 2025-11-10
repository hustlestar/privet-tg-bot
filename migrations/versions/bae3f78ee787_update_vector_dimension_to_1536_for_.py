"""Update vector dimension to 1536 for OpenAI embeddings

Revision ID: bae3f78ee787
Revises: ed964017b907
Create Date: 2025-09-01 11:55:44.441920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'bae3f78ee787'
down_revision: Union[str, None] = 'ed964017b907'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old embedding column and recreate with new dimension
    op.drop_column('user_facts', 'embedding')
    op.add_column('user_facts', 
        sa.Column('embedding', Vector(1536), nullable=True)
    )
    
    # Note: Existing embeddings will be lost and need to be regenerated
    # This is necessary because the embedding dimension change requires
    # re-computing all embeddings with the new model


def downgrade() -> None:
    # Drop the new embedding column and recreate with old dimension
    op.drop_column('user_facts', 'embedding')
    op.add_column('user_facts', 
        sa.Column('embedding', Vector(384), nullable=True)
    )