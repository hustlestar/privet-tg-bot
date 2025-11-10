"""add_language_learning_tables

Revision ID: f3a4b5c6d7e8
Revises: 35087af8dbee
Create Date: 2025-11-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, None] = '35087af8dbee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add language learning tables."""

    # Create pronunciation_cache table first (no dependencies)
    op.create_table(
        'pronunciation_cache',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('word_text', sa.String(length=255), nullable=False, comment='The word or phrase'),
        sa.Column('normalized_form', sa.String(length=255), nullable=False, comment='Lowercase normalized form'),
        sa.Column('language_code', sa.String(length=10), nullable=False, comment='Language code (es, en, ru)'),
        sa.Column('voice_id', sa.String(length=100), nullable=False, comment='TTS voice identifier'),
        sa.Column('provider', sa.String(length=50), nullable=False, comment='TTS provider (openai, elevenlabs, google)'),
        sa.Column('audio_format', sa.String(length=20), nullable=False, server_default='mp3', comment='Audio file format'),
        sa.Column('audio_data', sa.Text(), nullable=False, comment='Base64 encoded audio data'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, comment='Size of decoded audio'),
        sa.Column('duration_seconds', sa.Integer(), nullable=True, comment='Audio duration'),
        sa.Column('sample_rate', sa.Integer(), nullable=True, comment='Audio sample rate'),
        sa.Column('ipa_pronunciation', sa.String(length=255), nullable=True, comment='IPA phonetic notation'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='1', comment='Times this cache was used'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for pronunciation_cache
    op.create_index(
        'idx_pronunciation_lookup',
        'pronunciation_cache',
        ['normalized_form', 'language_code', 'voice_id'],
        unique=True
    )
    op.create_index('idx_pronunciation_language', 'pronunciation_cache', ['language_code'])
    op.create_index('idx_pronunciation_usage', 'pronunciation_cache', ['usage_count'])

    # Create vocabulary_words table
    op.create_table(
        'vocabulary_words',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('word_text', sa.String(length=255), nullable=False, comment='The actual word or phrase'),
        sa.Column('normalized_form', sa.String(length=255), nullable=False, comment='Lowercase normalized form for matching'),
        sa.Column('target_language', sa.String(length=10), nullable=False, comment='Language of the word (es, en, ru)'),
        sa.Column('native_language', sa.String(length=10), nullable=False, comment="User's native language for translation"),
        sa.Column('translation', sa.Text(), nullable=True, comment='Simple translation'),
        sa.Column('part_of_speech', sa.String(length=50), nullable=True, comment='noun, verb, adjective, etc.'),
        sa.Column('difficulty_level', sa.String(length=10), nullable=True, comment='A1, A2, B1, B2, C1, C2'),
        sa.Column('example_sentence', sa.Text(), nullable=True, comment='Example usage'),
        sa.Column('example_translation', sa.Text(), nullable=True, comment='Translation of example'),
        sa.Column('pronunciation_ipa', sa.String(length=255), nullable=True, comment='IPA phonetic notation'),
        sa.Column('pronunciation_cache_id', sa.Integer(), sa.ForeignKey('pronunciation_cache.id', ondelete='SET NULL'), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, comment='Additional data (context, synonyms, etc.)'),
        sa.Column('added_from_message_id', sa.Integer(), sa.ForeignKey('conversation_messages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('times_reviewed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('times_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mastery_level', sa.Integer(), nullable=False, server_default='0', comment='0-5 stars'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review_at', sa.DateTime(timezone=True), nullable=True, comment='For spaced repetition'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for vocabulary_words
    op.create_index('idx_vocabulary_user_id', 'vocabulary_words', ['user_id'])
    op.create_index('idx_vocabulary_word_text', 'vocabulary_words', ['word_text'])
    op.create_index('idx_vocabulary_normalized', 'vocabulary_words', ['normalized_form'])
    op.create_index('idx_vocabulary_next_review', 'vocabulary_words', ['next_review_at'])
    op.create_index('idx_vocabulary_active', 'vocabulary_words', ['is_active'])

    # Create learning_sessions table
    op.create_table(
        'learning_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=False, comment='conversation, flashcard, quiz, review'),
        sa.Column('words_studied', postgresql.ARRAY(sa.Integer()), nullable=True, comment='Array of vocabulary_word IDs'),
        sa.Column('correct_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('incorrect_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duration_seconds', sa.Integer(), nullable=True, comment='Session duration'),
        sa.Column('xp_earned', sa.Integer(), nullable=False, server_default='0', comment='Experience points'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, comment='Additional session data'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for learning_sessions
    op.create_index('idx_learning_sessions_user_id', 'learning_sessions', ['user_id'])
    op.create_index('idx_learning_sessions_type', 'learning_sessions', ['session_type'])
    op.create_index('idx_learning_sessions_started', 'learning_sessions', ['started_at'])

    # Create user_language_settings table
    op.create_table(
        'user_language_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_language', sa.String(length=10), nullable=False, comment='Language being learned'),
        sa.Column('native_language', sa.String(length=10), nullable=False, comment="User's native language"),
        sa.Column('proficiency_level', sa.String(length=10), nullable=True, comment='A1, A2, B1, B2, C1, C2'),
        sa.Column('daily_word_goal', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('daily_streak', sa.Integer(), nullable=False, server_default='0', comment='Consecutive days'),
        sa.Column('total_xp', sa.Integer(), nullable=False, server_default='0', comment='Total experience points'),
        sa.Column('current_level', sa.Integer(), nullable=False, server_default='1', comment='Gamification level'),
        sa.Column('preferred_tts_voice', sa.String(length=100), nullable=True, comment='Preferred voice for pronunciation'),
        sa.Column('learning_preferences', postgresql.JSONB(), nullable=True, comment='Additional preferences'),
        sa.Column('last_active_date', sa.DateTime(timezone=True), nullable=True, comment='Last learning activity'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_language_settings_user_id')
    )

    # Create indexes for user_language_settings
    op.create_index('idx_user_language_settings_user_id', 'user_language_settings', ['user_id'], unique=True)
    op.create_index('idx_user_language_settings_target', 'user_language_settings', ['target_language'])


def downgrade() -> None:
    """Downgrade schema - Remove language learning tables."""

    # Drop tables in reverse order (to handle foreign keys)
    op.drop_index('idx_user_language_settings_target', 'user_language_settings')
    op.drop_index('idx_user_language_settings_user_id', 'user_language_settings')
    op.drop_table('user_language_settings')

    op.drop_index('idx_learning_sessions_started', 'learning_sessions')
    op.drop_index('idx_learning_sessions_type', 'learning_sessions')
    op.drop_index('idx_learning_sessions_user_id', 'learning_sessions')
    op.drop_table('learning_sessions')

    op.drop_index('idx_vocabulary_active', 'vocabulary_words')
    op.drop_index('idx_vocabulary_next_review', 'vocabulary_words')
    op.drop_index('idx_vocabulary_normalized', 'vocabulary_words')
    op.drop_index('idx_vocabulary_word_text', 'vocabulary_words')
    op.drop_index('idx_vocabulary_user_id', 'vocabulary_words')
    op.drop_table('vocabulary_words')

    op.drop_index('idx_pronunciation_usage', 'pronunciation_cache')
    op.drop_index('idx_pronunciation_language', 'pronunciation_cache')
    op.drop_index('idx_pronunciation_lookup', 'pronunciation_cache')
    op.drop_table('pronunciation_cache')
