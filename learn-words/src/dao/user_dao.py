import datetime
import json
from typing import Optional, Callable, List, Dict, Any

from src.dao.models import User, UserPlan, UserWordStats, ResponseMode, ExplanationLanguage


class UserDao:
    def __init__(self, pool):
        self.pool = pool

    async def create_user(self, user: User, callback: Optional[Callable[[], None]] = None) -> None:
        """Create a new user."""
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO users (user_id, learning_language, interface_language, response_mode, explanation_language, plan, timezone, notification_times, notification_times_count, telegram_handle)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (user_id) DO UPDATE SET
                    learning_language = EXCLUDED.learning_language,
                    interface_language = EXCLUDED.interface_language,
                    response_mode = EXCLUDED.response_mode,
                    explanation_language = EXCLUDED.explanation_language,
                    plan = EXCLUDED.plan,
                    timezone = EXCLUDED.timezone,
                    notification_times = EXCLUDED.notification_times,
                    notification_times_count = EXCLUDED.notification_times_count,
                    telegram_handle = COALESCE(EXCLUDED.telegram_handle, users.telegram_handle)
                RETURNING xmax;
                """,
                user.user_id,
                user.learning_language.lower() if user.learning_language else None,
                user.interface_language,
                user.response_mode.value,
                user.explanation_language.value,
                user.plan.value,
                user.timezone,
                (json.dumps(user.notification_times) if user.notification_times else None),
                user.notification_times_count,
                user.telegram_handle,
            )
            if record and record["xmax"] == 0 and callback:
                await callback()

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            if row:
                # Handle explanation_language field with fallback for existing users
                explanation_lang = row.get("explanation_language", "native")
                interface_lang = row.get("interface_language", "english")
                return User(
                    user_id=row["user_id"],
                    learning_language=row["learning_language"],
                    interface_language=interface_lang,
                    response_mode=ResponseMode(row["response_mode"]),
                    explanation_language=ExplanationLanguage(explanation_lang),
                    plan=UserPlan(row.get("plan", "free")),
                    timezone=row.get("timezone", "UTC"),
                    notification_times=(json.loads(row["notification_times"]) if row.get("notification_times") else []),
                    notification_times_count=row.get("notification_times_count", 0),
                    created_at=row["created_at"],
                    is_blocked=row.get("is_blocked", False),
                    telegram_handle=row.get("telegram_handle"),
                )
            return None

    async def get_user_word_stats(self, user_id: int, word_id: int) -> Optional[UserWordStats]:
        """Get user word stats by user ID and word ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM user_word_stats WHERE user_id = $1 AND word_id = $2",
                user_id,
                word_id,
            )
            if row:
                return UserWordStats(
                    user_id=row["user_id"],
                    word_id=row["word_id"],
                    total_attempts=row["total_attempts"],
                    correct_answers=row["correct_answers"],
                    last_seen=row["last_seen"],
                    is_marked_known=row["is_marked_known"],
                    is_hidden=row["is_hidden"],
                    added_at=row["added_at"],
                    repetition_level=row.get("repetition_level", 0),
                    next_review_at=row.get("next_review_at"),
                )
            return None

    async def update_user(self, user: User) -> None:
        """Update an existing user."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users SET
                    learning_language = $2,
                    interface_language = $3,
                    response_mode = $4,
                    explanation_language = $5,
                    plan = $6,
                    timezone = $7,
                    notification_times = $8,
                    notification_times_count = $9
                WHERE user_id = $1
                """,
                user.user_id,
                user.learning_language.lower() if user.learning_language else None,
                user.interface_language,
                user.response_mode.value,
                user.explanation_language.value,
                user.plan.value,
                user.timezone,
                (json.dumps(user.notification_times) if user.notification_times else None),
                user.notification_times_count,
            )

    async def update_user_response_mode(self, user_id: int, mode: ResponseMode) -> None:
        """Update user's response mode preference."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET response_mode = $1 WHERE user_id = $2",
                mode.value,
                user_id,
            )

    async def update_user_explanation_language(self, user_id: int, explanation_language: ExplanationLanguage) -> None:
        """Update user's explanation language preference."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET explanation_language = $1 WHERE user_id = $2",
                explanation_language.value,
                user_id,
            )

    async def update_user_interface_language(self, user_id: int, interface_language: str) -> None:
        """Update user's interface language preference."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET interface_language = $1 WHERE user_id = $2",
                interface_language,
                user_id,
            )

    async def update_user_learning_language(self, user_id: int, learning_language: str) -> None:
        """Update user's learning language preference."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET learning_language = $1 WHERE user_id = $2",
                learning_language.lower(),
                user_id,
            )

    async def get_last_word_added_date(self, user_id: int) -> Optional[datetime.datetime]:
        """Get the date the user last added a word to their vocabulary."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT MAX(added_at) as last_added
                FROM user_word_stats
                WHERE user_id = $1
                """,
                user_id,
            )
            return row["last_added"] if row else None

    async def get_all_users(self) -> List[User]:
        """Get all users from the database."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM users")
            return [
                User(
                    user_id=row["user_id"],
                    learning_language=row["learning_language"],
                    interface_language=row.get("interface_language", "english"),
                    response_mode=ResponseMode(row["response_mode"]),
                    explanation_language=ExplanationLanguage(row.get("explanation_language", "native")),
                    plan=UserPlan(row.get("plan", "free")),
                    timezone=row.get("timezone", "UTC"),
                    notification_times=(json.loads(row["notification_times"]) if row.get("notification_times") else []),
                    notification_times_count=row.get("notification_times_count", 0),
                    created_at=row["created_at"],
                    is_blocked=row.get("is_blocked", False),
                    telegram_handle=row.get("telegram_handle"),
                )
                for row in rows
            ]

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        async with self.pool.acquire() as conn:
            # Basic vocabulary stats
            vocab_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_words,
                    COUNT(*) FILTER (WHERE is_marked_known = TRUE) as known_words,
                    SUM(total_attempts) as total_attempts,
                    SUM(correct_answers) as total_correct
                FROM user_word_stats
                WHERE user_id = $1
                """,
                user_id,
            )

            # Recent activity (last 7 days)
            recent_activity = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as recent_attempts,
                    COUNT(*) FILTER (WHERE is_correct = TRUE) as recent_correct
                FROM training_attempts
                WHERE user_id = $1 AND attempted_at > NOW() - INTERVAL '7 days'
                """,
                user_id,
            )

            return {
                "total_words": vocab_stats["total_words"] or 0,
                "known_words": vocab_stats["known_words"] or 0,
                "total_attempts": vocab_stats["total_attempts"] or 0,
                "total_correct": vocab_stats["total_correct"] or 0,
                "recent_attempts": recent_activity["recent_attempts"] or 0,
                "recent_correct": recent_activity["recent_correct"] or 0,
            }

    async def mark_user_as_blocked(self, user_id: int) -> None:
        """Mark a user as blocked (they blocked the bot)."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users
                SET is_blocked = TRUE
                WHERE user_id = $1
                """,
                user_id,
            )

    async def update_telegram_handle(self, user_id: int, telegram_handle: str) -> None:
        """Update user's telegram handle."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users
                SET telegram_handle = $2
                WHERE user_id = $1
                """,
                user_id,
                telegram_handle,
            )
