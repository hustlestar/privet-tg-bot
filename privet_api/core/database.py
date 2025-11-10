"""Database connection and management for the API."""

import logging
from typing import Optional
import asyncpg
from asyncpg import Pool

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        """Initialize the database manager.
        
        Args:
            database_url: PostgreSQL connection URL
            pool_size: Number of connections in the pool
            max_overflow: Maximum overflow connections
        """
        self.database_url = self._convert_to_asyncpg_url(database_url)
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool: Optional[Pool] = None

    def _convert_to_asyncpg_url(self, url: str) -> str:
        """Convert database URL to asyncpg format."""
        if url.startswith("postgresql://"):
            return url
        elif url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://")
        return url

    async def setup(self) -> None:
        """Set up the database connection pool and ensure extensions."""
        logger.info("Setting up database connection pool")
        
        # Create connection pool
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=self.pool_size,
            max_queries=50000,
            max_inactive_connection_lifetime=300,
        )
        
        # Ensure pgvector extension
        await self._ensure_extensions()
        
        logger.info("Database setup completed successfully")

    async def _ensure_extensions(self) -> None:
        """Ensure required PostgreSQL extensions are installed."""
        async with self.pool.acquire() as conn:
            # Check and create pgvector extension
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                logger.info("pgvector extension ensured")
            except Exception as e:
                logger.warning(f"Could not create pgvector extension: {e}")

    async def close(self) -> None:
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def execute(self, query: str, *args) -> str:
        """Execute a query without returning results."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list:
        """Execute a query and return all results."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Execute a query and return a single row."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Execute a query and return a single value."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    def get_pool(self) -> Optional[Pool]:
        """Get the connection pool."""
        return self.pool