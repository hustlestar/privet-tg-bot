"""User progress tracking table for XP and level system."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.sql import func

from .base import metadata

user_progress_table = Table(
    "user_progress",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="User ID (one progress record per user)"
    ),
    Column(
        "total_xp",
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Total experience points earned"
    ),
    Column(
        "current_level",
        Integer,
        nullable=False,
        default=1,
        server_default="1",
        comment="Current level (1-100)"
    ),
    Column(
        "xp_to_next_level",
        Integer,
        nullable=False,
        default=100,
        server_default="100",
        comment="XP needed to reach next level"
    ),
    Column(
        "current_streak",
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Current daily learning streak"
    ),
    Column(
        "longest_streak",
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Longest daily learning streak achieved"
    ),
    Column(
        "total_study_time_seconds",
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Total study time in seconds"
    ),
    Column(
        "total_sessions",
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Total number of learning sessions"
    ),
    Column(
        "last_activity_date",
        DateTime(timezone=True),
        nullable=True,
        comment="Last date user was active (for streak tracking)"
    ),
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
user_progress_user_idx = Index("idx_user_progress_user_id", user_progress_table.c.user_id)
user_progress_level_idx = Index("idx_user_progress_level", user_progress_table.c.current_level)
