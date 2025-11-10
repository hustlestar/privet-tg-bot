"""Learning sessions table for tracking user learning activity."""

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
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func

from .base import metadata

learning_sessions_table = Table(
    "learning_sessions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
    Column("session_type", String(50), nullable=False, comment="conversation, flashcard, quiz, review"),
    Column("words_studied", ARRAY(Integer), nullable=True, comment="Array of vocabulary_word IDs"),
    Column("correct_count", Integer, nullable=False, default=0, server_default="0"),
    Column("incorrect_count", Integer, nullable=False, default=0, server_default="0"),
    Column("duration_seconds", Integer, nullable=True, comment="Session duration"),
    Column("xp_earned", Integer, nullable=False, default=0, server_default="0", comment="Experience points"),
    Column("metadata", JSONB, nullable=True, comment="Additional session data"),
    Column(
        "started_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
    Column(
        "ended_at",
        DateTime(timezone=True),
        nullable=True,
    ),
)

# Indexes for analytics queries
learning_sessions_user_idx = Index("idx_learning_sessions_user_id", learning_sessions_table.c.user_id)
learning_sessions_type_idx = Index("idx_learning_sessions_type", learning_sessions_table.c.session_type)
learning_sessions_started_idx = Index("idx_learning_sessions_started", learning_sessions_table.c.started_at)
