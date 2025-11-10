"""Repository for user operations."""

from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for user data operations."""

    async def create_user(
        self, 
        user_id: int, 
        username: Optional[str] = None, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """Create a new user."""
        async with self._pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                INSERT INTO users (user_id, username, language, created_at)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                user_id,
                username or f"user_{user_id}",
                language,
                datetime.utcnow(),
            )
            return dict(user)

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        async with self._pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1", 
                user_id
            )
            return dict(user) if user else None

    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        language: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update user information."""
        async with self._pool.acquire() as conn:
            # Build update query dynamically
            updates = []
            params = []
            param_count = 1
            
            if username is not None:
                updates.append(f"username = ${param_count}")
                params.append(username)
                param_count += 1
            
            if language is not None:
                updates.append(f"language = ${param_count}")
                params.append(language)
                param_count += 1
            
            if not updates:
                return await self.get_user(user_id)
            
            # Add updated_at
            updates.append(f"updated_at = ${param_count}")
            params.append(datetime.utcnow())
            param_count += 1
            
            # Add user_id for WHERE clause
            params.append(user_id)
            
            query = f"""
                UPDATE users 
                SET {', '.join(updates)}
                WHERE user_id = ${param_count}
                RETURNING *
            """
            
            user = await conn.fetchrow(query, *params)
            return dict(user) if user else None

    async def delete_user(self, user_id: int) -> bool:
        """Delete user and cascade to related data."""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete related data first
                await conn.execute("DELETE FROM user_facts WHERE user_id = $1", user_id)
                await conn.execute("DELETE FROM user_profile_summaries WHERE user_id = $1", user_id)
                await conn.execute("DELETE FROM conversation_messages WHERE user_id = $1", user_id)
                
                # Delete user
                result = await conn.execute("DELETE FROM users WHERE user_id = $1", user_id)
                return result.split()[-1] != "0"

    async def ensure_user(
        self, 
        user_id: int, 
        username: Optional[str] = None, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """Ensure user exists, create if not."""
        user = await self.get_user(user_id)
        
        if user:
            # Update username if provided and different
            if username and user.get("username") != username:
                user = await self.update_user(user_id, username=username)
            return user
        else:
            return await self.create_user(user_id, username, language)

    async def get_user_count(self) -> int:
        """Get total number of users."""
        count = await self.fetchval("SELECT COUNT(*) FROM users")
        return count or 0

    async def get_users(
        self, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get users with pagination."""
        async with self._pool.acquire() as conn:
            users = await conn.fetch(
                """
                SELECT * FROM users 
                ORDER BY created_at DESC 
                LIMIT $1 OFFSET $2
                """,
                limit,
                offset
            )
            return [dict(user) for user in users]

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        async with self._pool.acquire() as conn:
            # Get message counts
            message_count = await conn.fetchval(
                "SELECT COUNT(*) FROM conversation_messages WHERE user_id = $1",
                user_id
            )
            
            voice_count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM conversation_messages 
                WHERE user_id = $1 AND transcribed_text IS NOT NULL
                """,
                user_id
            )
            
            # Get facts count
            facts_count = await conn.fetchval(
                "SELECT COUNT(*) FROM user_facts WHERE user_id = $1",
                user_id
            )
            
            # Get summaries count
            summaries_count = await conn.fetchval(
                "SELECT COUNT(*) FROM user_profile_summaries WHERE user_id = $1",
                user_id
            )
            
            # Get last activity
            last_message = await conn.fetchval(
                "SELECT MAX(created_at) FROM conversation_messages WHERE user_id = $1",
                user_id
            )
            
            return {
                "user_id": user_id,
                "total_messages": message_count or 0,
                "total_voice_messages": voice_count or 0,
                "total_facts": facts_count or 0,
                "profile_summaries": summaries_count or 0,
                "memory_density": (facts_count or 0) / max(message_count or 1, 1),
                "last_active": last_message
            }

    async def get_language_distribution(self) -> Dict[str, int]:
        """Get user count by language."""
        async with self._pool.acquire() as conn:
            stats = await conn.fetch(
                "SELECT language, COUNT(*) as count FROM users GROUP BY language"
            )
            return {row["language"]: row["count"] for row in stats}