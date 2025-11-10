"""Repository for user profile summary operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class ProfileRepository(BaseRepository):
    """Repository for user profile summaries."""

    async def create_or_update_summary(
        self,
        user_id: int,
        summary_text: str,
        summary_topic: str = "general",
    ) -> Dict[str, Any]:
        """Create or update a user profile summary."""
        async with self._pool.acquire() as conn:
            # Check if summary for this topic already exists
            existing = await conn.fetchrow(
                """
                SELECT * FROM user_profile_summaries 
                WHERE user_id = $1 AND summary_topic = $2
                """,
                user_id,
                summary_topic,
            )
            
            if existing:
                # Update existing summary
                summary = await conn.fetchrow(
                    """
                    UPDATE user_profile_summaries 
                    SET summary_text = $1, last_updated = $2 
                    WHERE id = $3
                    RETURNING *
                    """,
                    summary_text,
                    datetime.utcnow(),
                    existing["id"],
                )
            else:
                # Create new summary
                summary = await conn.fetchrow(
                    """
                    INSERT INTO user_profile_summaries 
                    (user_id, summary_text, summary_topic, last_updated, created_at)
                    VALUES ($1, $2, $3, $4, $4)
                    RETURNING *
                    """,
                    user_id,
                    summary_text,
                    summary_topic,
                    datetime.utcnow(),
                )
            
            return dict(summary)

    async def get_summary(
        self,
        user_id: int,
        summary_topic: str = "general"
    ) -> Optional[Dict[str, Any]]:
        """Get specific summary for a user by topic."""
        async with self._pool.acquire() as conn:
            summary = await conn.fetchrow(
                """
                SELECT * FROM user_profile_summaries 
                WHERE user_id = $1 AND summary_topic = $2
                """,
                user_id,
                summary_topic,
            )
            return dict(summary) if summary else None

    async def get_user_summaries(
        self,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all summaries for a user."""
        async with self._pool.acquire() as conn:
            query = """
                SELECT * FROM user_profile_summaries 
                WHERE user_id = $1 
                ORDER BY last_updated DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            summaries = await conn.fetch(query, user_id)
            return [dict(summary) for summary in summaries]

    async def get_recent_summaries(
        self,
        user_id: int,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get summaries updated within the last N days."""
        async with self._pool.acquire() as conn:
            summaries = await conn.fetch(
                """
                SELECT * FROM user_profile_summaries 
                WHERE user_id = $1 
                AND last_updated > NOW() - INTERVAL '%s days'
                ORDER BY last_updated DESC
                """ % days,
                user_id,
            )
            return [dict(summary) for summary in summaries]

    async def update_summary(
        self,
        user_id: int,
        summary_topic: str,
        summary_text: str
    ) -> bool:
        """Update an existing summary."""
        result = await self.execute(
            """
            UPDATE user_profile_summaries 
            SET summary_text = $1, last_updated = $2 
            WHERE user_id = $3 AND summary_topic = $4
            """,
            summary_text,
            datetime.utcnow(),
            user_id,
            summary_topic,
        )
        return result.split()[-1] != "0"

    async def delete_summary(
        self,
        user_id: int,
        summary_topic: str
    ) -> bool:
        """Delete a specific summary."""
        result = await self.execute(
            """
            DELETE FROM user_profile_summaries 
            WHERE user_id = $1 AND summary_topic = $2
            """,
            user_id,
            summary_topic,
        )
        return result.split()[-1] != "0"

    async def delete_user_summaries(self, user_id: int) -> int:
        """Delete all summaries for a user."""
        result = await self.execute(
            "DELETE FROM user_profile_summaries WHERE user_id = $1",
            user_id
        )
        parts = result.split()
        return int(parts[-1]) if len(parts) > 1 else 0

    async def get_summary_topics(self, user_id: int) -> List[str]:
        """Get all summary topics for a user."""
        async with self._pool.acquire() as conn:
            topics = await conn.fetch(
                """
                SELECT DISTINCT summary_topic 
                FROM user_profile_summaries 
                WHERE user_id = $1 
                ORDER BY summary_topic
                """,
                user_id,
            )
            return [row["summary_topic"] for row in topics]

    async def get_profile_context(
        self,
        user_id: int,
        max_summaries: int = 5
    ) -> List[Dict[str, Any]]:
        """Get profile summaries formatted for conversation context."""
        async with self._pool.acquire() as conn:
            summaries = await conn.fetch(
                """
                SELECT 
                    summary_topic,
                    summary_text,
                    last_updated
                FROM user_profile_summaries 
                WHERE user_id = $1 
                ORDER BY 
                    CASE summary_topic 
                        WHEN 'general' THEN 0 
                        ELSE 1 
                    END,
                    last_updated DESC 
                LIMIT $2
                """,
                user_id,
                max_summaries,
            )
            return [dict(summary) for summary in summaries]

    async def get_summary_count(self, user_id: int) -> int:
        """Get total summary count for a user."""
        count = await self.fetchval(
            "SELECT COUNT(*) FROM user_profile_summaries WHERE user_id = $1",
            user_id
        )
        return count or 0

    async def needs_update(
        self,
        user_id: int,
        summary_topic: str = "general",
        hours_threshold: int = 24
    ) -> bool:
        """Check if a summary needs updating based on age."""
        async with self._pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*) FROM user_profile_summaries 
                WHERE user_id = $1 
                AND summary_topic = $2
                AND last_updated > NOW() - INTERVAL '%s hours'
                """ % hours_threshold,
                user_id,
                summary_topic
            )
            return result == 0  # Needs update if no recent summary exists