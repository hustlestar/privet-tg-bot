"""Conversation messages table definition."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    Text,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import metadata

conversation_messages_table = Table(
    "conversation_messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
    Column("message_text", Text, nullable=True),
    Column("transcribed_text", Text, nullable=True),
    Column("sentiment_score", Float, nullable=True),
    Column("raw_telegram_message", JSONB, nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
)