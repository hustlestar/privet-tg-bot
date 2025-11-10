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
from .vocabulary_words import vocabulary_words_table
from .pronunciation_cache import pronunciation_cache_table
from .learning_sessions import learning_sessions_table
from .user_language_settings import user_language_settings_table

__all__ = [
    "metadata",
    "users_table",
    "conversation_messages_table",
    "user_facts_table",
    "user_profile_summaries_table",
    "vocabulary_words_table",
    "pronunciation_cache_table",
    "learning_sessions_table",
    "user_language_settings_table",
]
