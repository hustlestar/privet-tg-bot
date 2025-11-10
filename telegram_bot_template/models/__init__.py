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
from .pronunciation_cache import pronunciation_cache_table
from .learning_sessions import learning_sessions_table
from .user_language_settings import user_language_settings_table
from .grammar_rules import grammar_rules_table
from .user_progress import user_progress_table
from .achievements import achievements_table, user_achievements_table

__all__ = [
    "metadata",
    "users_table",
    "conversation_messages_table",
    "user_facts_table",
    "user_profile_summaries_table",
    "pronunciation_cache_table",
    "learning_sessions_table",
    "user_language_settings_table",
    "grammar_rules_table",
    "user_progress_table",
    "achievements_table",
    "user_achievements_table",
]
