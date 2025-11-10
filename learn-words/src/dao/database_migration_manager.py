import logging

import asyncpg

from src.config import get_config

logger = logging.getLogger(__name__)


async def _run_migration(conn, file_path, migration_name):
    """Run a single migration file with proper error handling.

    Args:
        conn: Database connection
        file_path: Path to the migration SQL file
        migration_name: Name of the migration for logging purposes
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            migration_content = f.read()

        if not migration_content.strip():
            logger.debug(f"Migration file '{file_path}' is empty, skipping.")
            return

        statements = [stmt.strip() for stmt in migration_content.split(";") if stmt.strip()]

        for statement in statements:
            try:
                await conn.execute(statement)
            except asyncpg.exceptions.DuplicateObjectError as e:
                # Ignore errors for objects that already exist
                logger.debug(f"Database object already exists (ignoring): {e}")
            except Exception as e:
                # Log other errors but don't fail startup
                logger.warning(f"{migration_name} migration warning: {e}")

    except FileNotFoundError:
        logger.warning(f"{migration_name} migration file not found, skipping...")
    except Exception as e:
        logger.error(f"Error running {migration_name} migration: {e}")


class DatabaseMigrationManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Initialize database connection pool and run migrations."""
        config = get_config()
        self.pool = await asyncpg.create_pool(config.database_url)

        # Run migrations with error handling for existing objects
        async with self.pool.acquire() as conn:
            try:
                await self._run_all_migrations(conn)
            except Exception as e:
                logger.error(f"Error running database migrations: {e}")
                # Don't raise the error - allow the bot to start even if migrations have issues

        return self.pool

    async def _run_all_migrations(self, conn):
        """Run all database migrations in sequence.

        Args:
            conn: Database connection
        """
        # Define all migrations with their file paths and names
        migrations = [
            ("migrations/init.sql", "Initial schema"),
            ("migrations/add_explanation_language.sql", "Explanation language"),
            ("migrations/add_interface_language.sql", "Interface language"),
            ("migrations/normalize_languages.sql", "Language normalization"),
            (
                "migrations/allow_null_learning_language.sql",
                "Allow null learning language",
            ),
            ("migrations/add_synonyms_columns.sql", "Add synonyms columns"),
            ("migrations/add_native_language.sql", "Add native language"),
            ("migrations/add_plan_and_timezone.sql", "Add plan and timezone"),
            ("migrations/add_word_fetching_indexes.sql", "Word fetching indexes"),
            ("migrations/add_is_hidden_to_user_word_stats.sql", "Is hidden"),
            ("migrations/add_repetition_fields.sql", "Repetition fields"),
            (
                "migrations/add_due_word_notifications_table.sql",
                "Due word notifications table",
            ),
            ("migrations/add_notifications_tracking.sql", "Notifications tracking"),
            (
                "migrations/add_user_notification_settings.sql",
                "User notification settings",
            ),
            (
                "migrations/add_message_id_to_notifications.sql",
                "Add message_id to notifications",
            ),
            ("migrations/add_notification_counts_and_types.sql", "Add notification counts and types"),
            ("migrations/update_notification_system.sql", "Update notification system"),
            (
                "migrations/add_synonym_training_type.sql",
                "Add synonym training type",
            ),
            (
                "migrations/remove_native_language_from_users.sql",
                "Remove native language from users",
            ),
            (
                "migrations/remove_success_rate_column.sql",
                "Remove success rate column",
            ),
            (
                "migrations/add_blocked_and_telegram_handle.sql",
                "Add is_blocked and telegram_handle fields",
            ),
        ]

        # Run each migration in sequence
        for file_path, migration_name in migrations:
            await _run_migration(conn, file_path, migration_name)
