"""Base repository class for database operations."""

import asyncpg
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base class for all repositories."""

    def __init__(self, pool: asyncpg.Pool):
        """Initialize repository with database pool.
        
        Args:
            pool: AsyncPG connection pool
        """
        self._pool = pool

    async def execute(self, query: str, *args) -> str:
        """Execute a query without returning results."""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Execute a query and return all results."""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Execute a query and return a single row."""
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Execute a query and return a single value."""
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)