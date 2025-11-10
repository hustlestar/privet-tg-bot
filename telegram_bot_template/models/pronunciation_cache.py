"""Pronunciation cache table for storing TTS audio to reduce API costs."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Index,
)
from sqlalchemy.sql import func

from .base import metadata

pronunciation_cache_table = Table(
    "pronunciation_cache",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("word_text", String(255), nullable=False, comment="The word or phrase"),
    Column("normalized_form", String(255), nullable=False, comment="Lowercase normalized form"),
    Column("language_code", String(10), nullable=False, comment="Language code (es, en, ru)"),
    Column("voice_id", String(100), nullable=False, comment="TTS voice identifier"),
    Column("provider", String(50), nullable=False, comment="TTS provider (openai, elevenlabs, google)"),
    Column("audio_format", String(20), nullable=False, default="mp3", comment="Audio file format"),
    Column("audio_data", Text, nullable=False, comment="Base64 encoded audio data"),
    Column("file_size_bytes", Integer, nullable=False, comment="Size of decoded audio"),
    Column("duration_seconds", Integer, nullable=True, comment="Audio duration"),
    Column("sample_rate", Integer, nullable=True, comment="Audio sample rate"),
    Column("ipa_pronunciation", String(255), nullable=True, comment="IPA phonetic notation"),
    Column("usage_count", Integer, nullable=False, default=1, server_default="1", comment="Times this cache was used"),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
    Column(
        "last_used_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
)

# Indexes for efficient cache lookups
pronunciation_lookup_idx = Index(
    "idx_pronunciation_lookup",
    pronunciation_cache_table.c.normalized_form,
    pronunciation_cache_table.c.language_code,
    pronunciation_cache_table.c.voice_id,
    unique=True,
)
pronunciation_language_idx = Index("idx_pronunciation_language", pronunciation_cache_table.c.language_code)
pronunciation_usage_idx = Index("idx_pronunciation_usage", pronunciation_cache_table.c.usage_count)
