"""Database models for the Telegram bot template.

This module contains SQLAlchemy Core table definitions used by Alembic
for database migrations. The actual database operations continue to use
asyncpg for performance and simplicity.
"""

from .base import metadata
from .users import users_table
from .conversation_messages import conversation_messages_table
from .user_facts import user_facts_table
from .user_profile_summaries import user_profile_summaries_table

__all__ = [
    "metadata",
    "users_table",
    "conversation_messages_table",
    "user_facts_table",
    "user_profile_summaries_table",
]

__all__ = [
    "metadata",
    "users_table",
]
