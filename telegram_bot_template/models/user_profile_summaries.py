"""User profile summaries table definition."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    Text,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func

from .base import metadata

user_profile_summaries_table = Table(
    "user_profile_summaries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True),
    Column("summary_text", Text, nullable=False),
    Column("summary_topic", String(255), nullable=False),
    Column(
        "last_updated",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
)