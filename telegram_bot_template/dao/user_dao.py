"""DAO for users table."""

from datetime import datetime
from typing import Optional, Dict, Any, List

from .base_dao import BaseDAO


class UserDAO(BaseDAO):
    """Data Access Object for users."""

    async def ensure_user(self, user_id: int, username: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        """Ensure user exists in database, create if not exists."""
        async with self._pool.acquire() as conn:
            # Try to get existing user
            user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

            if user:
                # Update username if provided and different
                if username and user["username"] != username:
                    await conn.execute(
                        "UPDATE users SET username = $1, updated_at = $2 WHERE user_id = $3",
                        username,
                        datetime.utcnow(),
                        user_id,
                    )
                return dict(user)
            else:
                # Create new user
                await conn.execute(
                    """
                    INSERT INTO users (user_id, username, language, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $4)
                    """,
                    user_id,
                    username,
                    language,
                    datetime.utcnow(),
                )

                # Get the created user
                user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
                return dict(user)

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        async with self._pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            return dict(user) if user else None

    async def update_user_language(self, user_id: int, language: str) -> bool:
        """Update user's language preference."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE users SET language = $1, updated_at = $2 WHERE user_id = $3",
                language,
                datetime.utcnow(),
                user_id,
            )
            return result.split()[-1] == "1"

    async def get_user_language(self, user_id: int) -> str:
        """Get user's language preference."""
        async with self._pool.acquire() as conn:
            language = await conn.fetchval("SELECT language FROM users WHERE user_id = $1", user_id)
            return language or "en"

    async def get_user_count(self) -> int:
        """Get total number of users."""
        async with self._pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM users")
            return count or 0

    async def get_users_by_language(self, language: str) -> int:
        """Get number of users by language."""
        async with self._pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM users WHERE language = $1", language)
            return count or 0

    async def get_recent_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently registered users."""
        async with self._pool.acquire() as conn:
            users = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC LIMIT $1", limit)
            return [dict(user) for user in users]

    async def delete_user(self, user_id: int) -> bool:
        """Delete user from database."""
        async with self._pool.acquire() as conn:
            result = await conn.execute("DELETE FROM users WHERE user_id = $1", user_id)
            return result.split()[-1] == "1"

    async def get_stats(self) -> Dict[str, Any]:
        """Get basic database statistics related to users."""
        async with self._pool.acquire() as conn:
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            language_stats = await conn.fetch("SELECT language, COUNT(*) as count FROM users GROUP BY language")
            recent_users = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '24 hours'"
            )
            return {
                "total_users": total_users or 0,
                "recent_users_24h": recent_users or 0,
                "language_distribution": {row["language"]: row["count"] for row in language_stats},
            }