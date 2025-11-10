"""DAO for user_profile_summaries table."""

from typing import Optional, Dict, Any, List
from datetime import datetime

from .base_dao import BaseDAO


class UserProfileSummaryDAO(BaseDAO):
    """Data Access Object for user profile summaries."""

    async def create_summary(
        self,
        user_id: int,
        summary_text: str,
        summary_topic: str,
    ) -> Dict[str, Any]:
        """Create a new user profile summary."""
        async with self._pool.acquire() as conn:
            # Check if summary for this topic already exists
            existing = await conn.fetchrow(
                "SELECT * FROM user_profile_summaries WHERE user_id = $1 AND summary_topic = $2",
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
                    INSERT INTO user_profile_summaries (user_id, summary_text, summary_topic)
                    VALUES ($1, $2, $3)
                    RETURNING *
                    """,
                    user_id,
                    summary_text,
                    summary_topic,
                )
            return dict(summary)

    async def get_summary(
        self, user_id: int, summary_topic: str
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
        self, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all summaries for a user."""
        async with self._pool.acquire() as conn:
            summaries = await conn.fetch(
                """
                SELECT * FROM user_profile_summaries 
                WHERE user_id = $1 
                ORDER BY last_updated DESC
                """,
                user_id,
            )
            return [dict(summary) for summary in summaries]

    async def get_recent_summaries(
        self, user_id: int, since_days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get summaries updated within the last N days."""
        async with self._pool.acquire() as conn:
            summaries = await conn.fetch(
                """
                SELECT * FROM user_profile_summaries 
                WHERE user_id = $1 
                AND last_updated > NOW() - INTERVAL '%s days'
                ORDER BY last_updated DESC
                """,
                since_days,
                user_id,
            )
            return [dict(summary) for summary in summaries]

    async def update_summary(
        self, user_id: int, summary_topic: str, summary_text: str
    ) -> bool:
        """Update an existing summary."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
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
            return result.split()[-1] == "1"

    async def delete_summary(
        self, user_id: int, summary_topic: str
    ) -> bool:
        """Delete a specific summary."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM user_profile_summaries 
                WHERE user_id = $1 AND summary_topic = $2
                """,
                user_id,
                summary_topic,
            )
            return result.split()[-1] == "1"

    async def delete_user_summaries(self, user_id: int) -> int:
        """Delete all summaries for a user (GDPR compliance)."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM user_profile_summaries WHERE user_id = $1", user_id
            )
            return int(result.split()[-1])

    async def get_topics(self, user_id: int) -> List[str]:
        """Get all summary topics for a user."""
        async with self._pool.acquire() as conn:
            topics = await conn.fetch(
                """
                SELECT summary_topic 
                FROM user_profile_summaries 
                WHERE user_id = $1 
                ORDER BY summary_topic
                """,
                user_id,
            )
            return [row["summary_topic"] for row in topics]

    async def get_profile_context(
        self, user_id: int, max_summaries: int = 5
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
                ORDER BY last_updated DESC 
                LIMIT $2
                """,
                user_id,
                max_summaries,
            )
            return [dict(summary) for summary in summaries]