"""add_grammar_progress_achievements

Revision ID: a1b2c3d4e5f6
Revises: f3a4b5c6d7e8
Create Date: 2025-11-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add grammar rules, user progress, and achievements tables."""

    # Create grammar_rules table
    op.create_table(
        'grammar_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rule_code', sa.String(length=100), nullable=False, unique=True, comment='Unique identifier like "es_present_tense_regular"'),
        sa.Column('language', sa.String(length=10), nullable=False, comment='Target language (es, en, ru)'),
        sa.Column('category', sa.String(length=100), nullable=False, comment='Category: tense, mood, article, adjective, etc.'),
        sa.Column('difficulty_level', sa.String(length=10), nullable=False, comment='CEFR level: A1, A2, B1, B2, C1, C2'),
        sa.Column('title_en', sa.String(length=255), nullable=False, comment='Rule title in English'),
        sa.Column('title_es', sa.String(length=255), nullable=True, comment='Rule title in Spanish'),
        sa.Column('title_ru', sa.String(length=255), nullable=True, comment='Rule title in Russian'),
        sa.Column('description_en', sa.Text(), nullable=False, comment='Full explanation in English'),
        sa.Column('description_es', sa.Text(), nullable=True, comment='Full explanation in Spanish'),
        sa.Column('description_ru', sa.Text(), nullable=True, comment='Full explanation in Russian'),
        sa.Column('examples', postgresql.JSONB(), nullable=True, comment='Array of example objects with text and translations'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True, comment='Search tags'),
        sa.Column('related_rules', postgresql.ARRAY(sa.String()), nullable=True, comment='Related rule codes'),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0', comment='Display order within category'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for grammar_rules
    op.create_index('idx_grammar_rules_language', 'grammar_rules', ['language'])
    op.create_index('idx_grammar_rules_category', 'grammar_rules', ['category'])
    op.create_index('idx_grammar_rules_difficulty', 'grammar_rules', ['difficulty_level'])
    op.create_index('idx_grammar_rules_active', 'grammar_rules', ['is_active'])

    # Create user_progress table
    op.create_table(
        'user_progress',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, comment='User ID (one progress record per user)'),
        sa.Column('total_xp', sa.Integer(), nullable=False, server_default='0', comment='Total experience points earned'),
        sa.Column('current_level', sa.Integer(), nullable=False, server_default='1', comment='Current level (1-100)'),
        sa.Column('xp_to_next_level', sa.Integer(), nullable=False, server_default='100', comment='XP needed to reach next level'),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0', comment='Current daily learning streak'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0', comment='Longest daily learning streak achieved'),
        sa.Column('total_study_time_seconds', sa.Integer(), nullable=False, server_default='0', comment='Total study time in seconds'),
        sa.Column('total_sessions', sa.Integer(), nullable=False, server_default='0', comment='Total number of learning sessions'),
        sa.Column('last_activity_date', sa.DateTime(timezone=True), nullable=True, comment='Last date user was active (for streak tracking)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_progress_user_id')
    )

    # Create indexes for user_progress
    op.create_index('idx_user_progress_user_id', 'user_progress', ['user_id'], unique=True)
    op.create_index('idx_user_progress_level', 'user_progress', ['current_level'])

    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('achievement_code', sa.String(length=100), nullable=False, unique=True, comment='Unique code identifier (e.g., "first_session", "week_streak")'),
        sa.Column('title_en', sa.String(length=255), nullable=False, comment='Achievement title in English'),
        sa.Column('title_es', sa.String(length=255), nullable=True, comment='Achievement title in Spanish'),
        sa.Column('title_ru', sa.String(length=255), nullable=True, comment='Achievement title in Russian'),
        sa.Column('description_en', sa.Text(), nullable=False, comment='Achievement description in English'),
        sa.Column('description_es', sa.Text(), nullable=True, comment='Achievement description in Spanish'),
        sa.Column('description_ru', sa.Text(), nullable=True, comment='Achievement description in Russian'),
        sa.Column('icon', sa.String(length=50), nullable=True, comment='Icon name or emoji'),
        sa.Column('xp_reward', sa.Integer(), nullable=False, server_default='0', comment='XP awarded when achievement is earned'),
        sa.Column('category', sa.String(length=50), nullable=False, comment='Category: streak, session, milestone, special'),
        sa.Column('difficulty', sa.String(length=20), nullable=False, server_default="'bronze'", comment='Difficulty tier: bronze, silver, gold, platinum'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, comment='Additional achievement configuration'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', sa.Integer(), sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, comment='Context of when/how it was earned'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for user_achievements
    op.create_index('idx_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('idx_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])

    # Create unique constraint for user_achievements
    op.create_unique_constraint('uq_user_achievement', 'user_achievements', ['user_id', 'achievement_id'])


def downgrade() -> None:
    """Downgrade schema - Remove grammar, progress, and achievements tables."""

    # Drop tables in reverse order (to handle foreign keys)
    op.drop_constraint('uq_user_achievement', 'user_achievements', type_='unique')
    op.drop_index('idx_user_achievements_achievement_id', 'user_achievements')
    op.drop_index('idx_user_achievements_user_id', 'user_achievements')
    op.drop_table('user_achievements')

    op.drop_table('achievements')

    op.drop_index('idx_user_progress_level', 'user_progress')
    op.drop_index('idx_user_progress_user_id', 'user_progress')
    op.drop_table('user_progress')

    op.drop_index('idx_grammar_rules_active', 'grammar_rules')
    op.drop_index('idx_grammar_rules_difficulty', 'grammar_rules')
    op.drop_index('idx_grammar_rules_category', 'grammar_rules')
    op.drop_index('idx_grammar_rules_language', 'grammar_rules')
    op.drop_table('grammar_rules')
