"""User language settings and preferences for learning."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import metadata

user_language_settings_table = Table(
    "user_language_settings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("target_language", String(10), nullable=False, comment="Language being learned"),
    Column("native_language", String(10), nullable=False, comment="User's native language"),
    Column("proficiency_level", String(10), nullable=True, comment="A1, A2, B1, B2, C1, C2"),
    Column("daily_word_goal", Integer, nullable=False, default=10, server_default="10"),
    Column("daily_streak", Integer, nullable=False, default=0, server_default="0", comment="Consecutive days"),
    Column("total_xp", Integer, nullable=False, default=0, server_default="0", comment="Total experience points"),
    Column("current_level", Integer, nullable=False, default=1, server_default="1", comment="Gamification level"),
    Column("preferred_tts_voice", String(100), nullable=True, comment="Preferred voice for pronunciation"),
    Column("learning_preferences", JSONB, nullable=True, comment="Additional preferences"),
    Column("last_active_date", DateTime(timezone=True), nullable=True, comment="Last learning activity"),
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

# Indexes
user_language_settings_user_idx = Index("idx_user_language_settings_user_id", user_language_settings_table.c.user_id, unique=True)
user_language_settings_target_lang_idx = Index("idx_user_language_settings_target", user_language_settings_table.c.target_language)
