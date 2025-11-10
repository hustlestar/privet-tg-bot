"""API dependencies for dependency injection."""

from src.database import db


async def get_pool():
    """Get database connection pool.

    Returns:
        asyncpg.Pool: Database connection pool
    """
    return db.pool
