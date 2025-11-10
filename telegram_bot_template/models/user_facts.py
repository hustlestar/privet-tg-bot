"""User facts table definition for RAG service."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from .base import metadata

user_facts_table = Table(
    "user_facts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
    Column("fact_text", Text, nullable=False),
    Column("fact_summary", Text, nullable=True),
    Column(
        "source_message_id",
        Integer,
        ForeignKey("conversation_messages.id", ondelete="SET NULL"),
        nullable=True,
    ),
    Column("embedding", Vector(384)),  # Match the all-MiniLM-L6-v2 model dimension
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
)