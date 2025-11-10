"""Vocabulary words table definition for language learning."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import metadata

vocabulary_words_table = Table(
    "vocabulary_words",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
    Column("word_text", String(255), nullable=False, comment="The actual word or phrase"),
    Column("normalized_form", String(255), nullable=False, comment="Lowercase normalized form for matching"),
    Column("target_language", String(10), nullable=False, comment="Language of the word (es, en, ru)"),
    Column("native_language", String(10), nullable=False, comment="User's native language for translation"),
    Column("translation", Text, nullable=True, comment="Simple translation"),
    Column("part_of_speech", String(50), nullable=True, comment="noun, verb, adjective, etc."),
    Column("difficulty_level", String(10), nullable=True, comment="A1, A2, B1, B2, C1, C2"),
    Column("example_sentence", Text, nullable=True, comment="Example usage"),
    Column("example_translation", Text, nullable=True, comment="Translation of example"),
    Column("pronunciation_ipa", String(255), nullable=True, comment="IPA phonetic notation"),
    Column("pronunciation_cache_id", Integer, ForeignKey("pronunciation_cache.id", ondelete="SET NULL"), nullable=True),
    Column("metadata", JSONB, nullable=True, comment="Additional data (context, synonyms, etc.)"),
    Column("added_from_message_id", Integer, ForeignKey("conversation_messages.id", ondelete="SET NULL"), nullable=True),
    Column("times_reviewed", Integer, nullable=False, default=0, server_default="0"),
    Column("times_correct", Integer, nullable=False, default=0, server_default="0"),
    Column("mastery_level", Integer, nullable=False, default=0, server_default="0", comment="0-5 stars"),
    Column("is_active", Boolean, nullable=False, default=True, server_default="true"),
    Column("last_reviewed_at", DateTime(timezone=True), nullable=True),
    Column("next_review_at", DateTime(timezone=True), nullable=True, comment="For spaced repetition"),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    ),
)

# Indexes for better query performance
vocabulary_user_idx = Index("idx_vocabulary_user_id", vocabulary_words_table.c.user_id)
vocabulary_word_idx = Index("idx_vocabulary_word_text", vocabulary_words_table.c.word_text)
vocabulary_normalized_idx = Index("idx_vocabulary_normalized", vocabulary_words_table.c.normalized_form)
vocabulary_review_idx = Index("idx_vocabulary_next_review", vocabulary_words_table.c.next_review_at)
vocabulary_active_idx = Index("idx_vocabulary_active", vocabulary_words_table.c.is_active)
