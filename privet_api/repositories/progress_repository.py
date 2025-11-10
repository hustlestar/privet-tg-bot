"""Repository for user progress tracking operations."""

import logging
from typing import Optional, List
from datetime import datetime, timedelta
import asyncpg

logger = logging.getLogger(__name__)


class ProgressRepository:
    """Handles database operations for user progress and achievements."""

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with database connection pool."""
        self.pool = pool

    async def get_user_progress(self, user_id: int) -> Optional[asyncpg.Record]:
        """Get user's current progress.

        Args:
            user_id: User ID

        Returns:
            Progress record or None
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT *
                FROM user_progress
                WHERE user_id = $1
                """,
                user_id
            )

    async def create_or_get_progress(self, user_id: int) -> asyncpg.Record:
        """Create progress record if it doesn't exist, otherwise return existing.

        Args:
            user_id: User ID

        Returns:
            Progress record
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO user_progress (user_id, total_xp, current_level, xp_to_next_level)
                VALUES ($1, 0, 1, 100)
                ON CONFLICT (user_id) DO UPDATE SET user_id = EXCLUDED.user_id
                RETURNING *
                """,
                user_id
            )

    async def add_xp(
        self,
        user_id: int,
        xp_amount: int,
        activity_type: str = "general"
    ) -> asyncpg.Record:
        """Add XP to user and handle level-ups.

        Args:
            user_id: User ID
            xp_amount: Amount of XP to add
            activity_type: Type of activity (for logging)

        Returns:
            Updated progress record
        """
        async with self.pool.acquire() as conn:
            # Ensure progress record exists
            await self.create_or_get_progress(user_id)

            # Add XP and update level if needed
            return await conn.fetchrow(
                """
                UPDATE user_progress
                SET
                    total_xp = total_xp + $2,
                    current_level = LEAST(100, 1 + FLOOR(POWER((total_xp + $2) / 100.0, 0.5))),
                    xp_to_next_level = POWER(current_level + 1, 2) * 100 - (total_xp + $2),
                    updated_at = NOW()
                WHERE user_id = $1
                RETURNING *
                """,
                user_id,
                xp_amount
            )

    async def update_streak(self, user_id: int) -> asyncpg.Record:
        """Update user's daily streak.

        Increments streak if active within 24 hours, resets if missed a day.

        Args:
            user_id: User ID

        Returns:
            Updated progress record
        """
        async with self.pool.acquire() as conn:
            # Ensure progress record exists
            await self.create_or_get_progress(user_id)

            # Get current progress
            progress = await self.get_user_progress(user_id)

            now = datetime.utcnow()
            last_activity = progress["last_activity_date"] if progress else None

            # Determine if streak continues or resets
            if last_activity:
                time_since_activity = now - last_activity

                # Same day - no change
                if time_since_activity < timedelta(hours=24) and last_activity.date() == now.date():
                    return progress

                # Next day - increment streak
                elif time_since_activity < timedelta(hours=48):
                    new_streak = progress["current_streak"] + 1
                    longest_streak = max(progress["longest_streak"], new_streak)

                # Missed a day - reset streak
                else:
                    new_streak = 1
                    longest_streak = progress["longest_streak"]
            else:
                # First activity ever
                new_streak = 1
                longest_streak = 1

            return await conn.fetchrow(
                """
                UPDATE user_progress
                SET
                    current_streak = $2,
                    longest_streak = $3,
                    last_activity_date = $4,
                    updated_at = NOW()
                WHERE user_id = $1
                RETURNING *
                """,
                user_id,
                new_streak,
                longest_streak,
                now
            )

    async def record_session(
        self,
        user_id: int,
        session_type: str,
        duration_seconds: int,
        xp_earned: int
    ) -> asyncpg.Record:
        """Record a learning session.

        Args:
            user_id: User ID
            session_type: Type of session
            duration_seconds: Duration in seconds
            xp_earned: XP earned this session

        Returns:
            Created session record
        """
        async with self.pool.acquire() as conn:
            # Create session
            session = await conn.fetchrow(
                """
                INSERT INTO learning_sessions (
                    user_id,
                    session_type,
                    duration_seconds,
                    xp_earned,
                    started_at,
                    ended_at
                )
                VALUES ($1, $2, $3, $4, NOW() - INTERVAL '1 second' * $3, NOW())
                RETURNING *
                """,
                user_id,
                session_type,
                duration_seconds,
                xp_earned
            )

            # Update total stats
            await conn.execute(
                """
                UPDATE user_progress
                SET
                    total_study_time_seconds = total_study_time_seconds + $2,
                    total_sessions = total_sessions + 1,
                    updated_at = NOW()
                WHERE user_id = $1
                """,
                user_id,
                duration_seconds
            )

            return session

    async def get_user_statistics(self, user_id: int) -> dict:
        """Get comprehensive user statistics.

        Args:
            user_id: User ID

        Returns:
            Dictionary of statistics
        """
        async with self.pool.acquire() as conn:
            progress = await self.get_user_progress(user_id)

            if not progress:
                progress = await self.create_or_get_progress(user_id)

            # Get session statistics
            session_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_sessions,
                    COALESCE(SUM(duration_seconds), 0) as total_time,
                    COALESCE(SUM(xp_earned), 0) as total_xp_from_sessions,
                    COALESCE(AVG(duration_seconds), 0) as avg_session_duration
                FROM learning_sessions
                WHERE user_id = $1
                """,
                user_id
            )

            return {
                "user_id": user_id,
                "total_xp": progress["total_xp"],
                "current_level": progress["current_level"],
                "xp_to_next_level": progress["xp_to_next_level"],
                "current_streak": progress["current_streak"],
                "longest_streak": progress["longest_streak"],
                "total_study_time_seconds": progress["total_study_time_seconds"],
                "total_sessions": progress["total_sessions"],
                "last_activity_date": progress["last_activity_date"],
                "avg_session_duration": int(session_stats["avg_session_duration"]),
                "created_at": progress["created_at"],
            }

    # Achievement methods

    async def get_all_achievements(self) -> List[asyncpg.Record]:
        """Get all available achievements.

        Returns:
            List of achievement records
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT *
                FROM achievements
                WHERE is_active = true
                ORDER BY category, difficulty, achievement_code
                """
            )

    async def get_user_achievements(self, user_id: int) -> List[asyncpg.Record]:
        """Get achievements earned by user.

        Args:
            user_id: User ID

        Returns:
            List of earned achievements with details
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT
                    a.*,
                    ua.earned_at,
                    ua.metadata as earned_metadata
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.user_id = $1
                ORDER BY ua.earned_at DESC
                """,
                user_id
            )

    async def award_achievement(
        self,
        user_id: int,
        achievement_code: str,
        metadata: Optional[dict] = None
    ) -> Optional[asyncpg.Record]:
        """Award an achievement to a user.

        Args:
            user_id: User ID
            achievement_code: Achievement code
            metadata: Optional metadata about earning context

        Returns:
            Achievement record if newly awarded, None if already had it
        """
        async with self.pool.acquire() as conn:
            # Get achievement
            achievement = await conn.fetchrow(
                """
                SELECT * FROM achievements
                WHERE achievement_code = $1 AND is_active = true
                """,
                achievement_code
            )

            if not achievement:
                logger.warning(f"Achievement not found: {achievement_code}")
                return None

            # Check if already awarded
            existing = await conn.fetchrow(
                """
                SELECT * FROM user_achievements
                WHERE user_id = $1 AND achievement_id = $2
                """,
                user_id,
                achievement["id"]
            )

            if existing:
                return None

            # Award achievement
            await conn.execute(
                """
                INSERT INTO user_achievements (user_id, achievement_id, metadata)
                VALUES ($1, $2, $3)
                """,
                user_id,
                achievement["id"],
                metadata
            )

            # Award XP
            if achievement["xp_reward"] > 0:
                await self.add_xp(user_id, achievement["xp_reward"], "achievement")

            return achievement

    async def get_leaderboard(
        self,
        metric: str = "total_xp",
        limit: int = 100
    ) -> List[asyncpg.Record]:
        """Get leaderboard rankings.

        Args:
            metric: Metric to rank by (total_xp, current_level, longest_streak)
            limit: Number of users to return

        Returns:
            List of user progress records ordered by metric
        """
        valid_metrics = ["total_xp", "current_level", "longest_streak", "total_study_time_seconds"]
        if metric not in valid_metrics:
            metric = "total_xp"

        async with self.pool.acquire() as conn:
            query = f"""
                SELECT
                    up.*,
                    u.first_name,
                    u.last_name,
                    u.username
                FROM user_progress up
                JOIN users u ON up.user_id = u.user_id
                ORDER BY up.{metric} DESC
                LIMIT $1
            """

            return await conn.fetch(query, limit)
