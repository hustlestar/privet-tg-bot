"""User achievements table for gamification."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import metadata

# Achievement definitions (what can be earned)
achievements_table = Table(
    "achievements",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "achievement_code",
        String(100),
        nullable=False,
        unique=True,
        comment="Unique code identifier (e.g., 'first_session', 'week_streak')"
    ),
    Column(
        "title_en",
        String(255),
        nullable=False,
        comment="Achievement title in English"
    ),
    Column(
        "title_es",
        String(255),
        nullable=True,
        comment="Achievement title in Spanish"
    ),
    Column(
        "title_ru",
        String(255),
        nullable=True,
        comment="Achievement title in Russian"
    ),
    Column(
        "description_en",
        Text,
        nullable=False,
        comment="Achievement description in English"
    ),
    Column(
        "description_es",
        Text,
        nullable=True,
        comment="Achievement description in Spanish"
    ),
    Column(
        "description_ru",
        Text,
        nullable=True,
        comment="Achievement description in Russian"
    ),
    Column(
        "icon",
        String(50),
        nullable=True,
        comment="Icon name or emoji"
    ),
    Column(
        "xp_reward",
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="XP awarded when achievement is earned"
    ),
    Column(
        "category",
        String(50),
        nullable=False,
        comment="Category: streak, session, milestone, special"
    ),
    Column(
        "difficulty",
        String(20),
        nullable=False,
        default="bronze",
        server_default="'bronze'",
        comment="Difficulty tier: bronze, silver, gold, platinum"
    ),
    Column(
        "is_active",
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    ),
    Column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Additional achievement configuration"
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
)

# User achievements (what users have earned)
user_achievements_table = Table(
    "user_achievements",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "achievement_id",
        Integer,
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "earned_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
    Column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Context of when/how it was earned"
    ),
)

# Constraints and indexes
user_achievements_unique = UniqueConstraint(
    user_achievements_table.c.user_id,
    user_achievements_table.c.achievement_id,
    name="uq_user_achievement"
)

user_achievements_user_idx = Index(
    "idx_user_achievements_user_id",
    user_achievements_table.c.user_id
)

user_achievements_achievement_idx = Index(
    "idx_user_achievements_achievement_id",
    user_achievements_table.c.achievement_id
)
