"""Database management for the Telegram bot template."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

import asyncpg

from .migration_manager import MigrationManager
from .database_health import DatabaseHealthChecker

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager with automatic migration support."""

    def __init__(self, database_url: str, auto_migrate: bool = True):
        """Initialize the database manager.

        Args:
            database_url: PostgreSQL database connection URL
            auto_migrate: Whether to automatically apply pending migrations on setup
        """
        self.database_url = database_url
        self.auto_migrate = auto_migrate
        self._pool: Optional[asyncpg.Pool] = None
        self._migration_manager = MigrationManager(database_url)

    @classmethod
    def from_config(cls, config):
        """Create DatabaseManager from BotConfig.

        Args:
            config: BotConfig instance

        Returns:
            DatabaseManager instance
        """
        return cls(database_url=config.database_url, auto_migrate=config.auto_migrate)

    async def setup(self) -> None:
        """Initialize database connection and ensure schema is up to date."""
        try:
            # Ensure required database extensions are available
            logger.info("Ensuring database extensions are available...")
            health_checker = DatabaseHealthChecker(self.database_url)
            if not await health_checker.ensure_extensions():
                logger.warning("Some database extensions may not be available")
            
            # Run migrations first if auto_migrate is enabled
            if self.auto_migrate:
                logger.info("Checking for pending database migrations...")
                migration_success = await self._migration_manager.ensure_database_ready(auto_migrate=True)
                if not migration_success:
                    raise RuntimeError("Database migration failed")

            # Create connection pool
            # asyncpg expects DSN without the +asyncpg dialect part
            asyncpg_compatible_dsn = self.database_url
            if "postgresql+asyncpg://" in asyncpg_compatible_dsn:
                asyncpg_compatible_dsn = asyncpg_compatible_dsn.replace("postgresql+asyncpg://", "postgresql://")
            
            self._pool = await asyncpg.create_pool(asyncpg_compatible_dsn)
            logger.info("Database setup completed successfully")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

    async def close(self) -> None:
        """Close database connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection closed")

    @property
    def migration_manager(self) -> MigrationManager:
        """Get the migration manager instance."""
        return self._migration_manager

    def create_migration(self, message: str, autogenerate: bool = True) -> str:
        """Create a new migration.

        Args:
            message: Migration description
            autogenerate: Whether to auto-generate migration from model changes

        Returns:
            Generated revision ID
        """
        return self._migration_manager.create_migration(message, autogenerate)

    def apply_migrations(self, target_revision: str = "head") -> bool:
        """Apply migrations to the database.

        Args:
            target_revision: Target revision to migrate to (default: "head")

        Returns:
            True if migrations were applied successfully, False otherwise
        """
        return self._migration_manager.apply_migrations(target_revision)

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status.

        Returns:
            Dictionary with migration status information
        """
        current = self._migration_manager.get_current_revision()
        head = self._migration_manager.get_head_revision()
        has_pending = self._migration_manager.has_pending_migrations()

        return {
            "current_revision": current,
            "head_revision": head,
            "has_pending_migrations": has_pending,
            "migration_history": self._migration_manager.get_migration_history(),
        }

    @property
    def pool(self) -> Optional[asyncpg.Pool]:
        """Get the connection pool."""
        return self._pool
