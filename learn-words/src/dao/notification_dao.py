import datetime
import json
import logging
from typing import Optional, List, Dict, Any

from src.repetition import get_next_review_date

logger = logging.getLogger(__name__)


class NotificationDao:
    def __init__(self, pool):
        self.pool = pool

    async def get_due_words_for_user(self, user_id: int, exclude_word_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Get words due for repetition for a user, prioritizing by repetition level
        and total attempts, and excluding words added today.
        """
        async with self.pool.acquire() as conn:
            params = [user_id]
            exclude_clause = ""
            if exclude_word_ids:
                # Use ANY($2) for safe list insertion
                exclude_clause = "AND NOT (uws.word_id = ANY($2))"
                params.append(exclude_word_ids)

            query = f"""
                SELECT
                    w.id as word_id,
                    w.word,
                    w.short_translation
                FROM user_word_stats uws
                JOIN words w ON uws.word_id = w.id
                WHERE uws.user_id = $1
                  AND (uws.next_review_at <= NOW() OR uws.next_review_at IS NULL)
                  AND uws.is_hidden = FALSE
                  AND DATE(uws.added_at) < CURRENT_DATE -- Exclude words added today
                  {exclude_clause}
                ORDER BY
                    uws.repetition_level ASC,
                    uws.total_attempts ASC,
                    uws.next_review_at ASC
                LIMIT 25;
            """
            rows = await conn.fetch(query, *params)
            return [
                {
                    "word_id": row["word_id"],
                    "word": row["word"],
                    "short_translation": row["short_translation"],
                }
                for row in rows
            ]

    async def get_pending_notification_word_ids(self, user_id: int) -> List[int]:
        """Get all word IDs from pending (un-responded) notifications for a user."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT jsonb_array_elements_text(word_ids) as word_id
                FROM due_word_notifications
                WHERE user_id = $1
                """,
                user_id,
            )
            return list({int(row["word_id"]) for row in rows})

    async def create_due_word_notification(self, user_id: int, word_ids: List[int]) -> int:
        """Create a due word notification and return its ID."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                """
                INSERT INTO due_word_notifications (user_id, word_ids)
                VALUES ($1, $2)
                RETURNING id;
                """,
                user_id,
                json.dumps(word_ids),
            )

    async def get_due_word_notification(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a due word notification by its ID, ensuring it's not older than 72 hours.
        This allows a user 3 days to respond to a notification.
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT user_id, word_ids, created_at FROM due_word_notifications
                WHERE id = $1 AND created_at >= NOW() - INTERVAL '72 hours'
                """,
                notification_id,
            )
            if row:
                return {
                    "user_id": row["user_id"],
                    "word_ids": json.loads(row["word_ids"]),
                    "created_at": row["created_at"],
                }
            return None

    async def delete_due_word_notification(self, notification_id: int) -> None:
        """Delete a due word notification by its ID."""
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM due_word_notifications WHERE id = $1", notification_id)

    async def batch_update_word_repetition_status(self, user_id: int, word_ids: List[int]) -> None:
        """Batch update repetition status for multiple words for a user."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Get current repetition levels for the given words
                rows = await conn.fetch(
                    """
                    SELECT word_id, repetition_level
                    FROM user_word_stats
                    WHERE user_id = $1 AND word_id = ANY($2::int[])
                    """,
                    user_id,
                    word_ids,
                )

                word_levels = {row["word_id"]: row["repetition_level"] for row in rows}

                updates = []
                for word_id in word_ids:
                    current_level = word_levels.get(word_id, 0)
                    new_level, next_review = get_next_review_date(current_level, is_correct=True)
                    updates.append((word_id, new_level, next_review))

                if not updates:
                    return

                # Separate the tuples into individual lists for the query
                update_word_ids, update_levels, update_reviews = zip(*updates)

                await conn.execute(
                    """
                    UPDATE user_word_stats uws
                    SET
                        repetition_level = new_data.repetition_level,
                        next_review_at = new_data.next_review_at
                    FROM (
                        SELECT
                            unnest($2::int[]) as word_id,
                            unnest($3::int[]) as repetition_level,
                            unnest($4::timestamp[]) as next_review_at
                    ) AS new_data
                    WHERE uws.user_id = $1 AND uws.word_id = new_data.word_id
                    """,
                    user_id,
                    list(update_word_ids),
                    list(update_levels),
                    list(update_reviews),
                )

    async def get_users_for_notification(self, notification_time: datetime.time, default_notification_time: datetime.time) -> List[int]:
        """
        Get user IDs for notification.
        - Users with a specific notification time set.
        - Users with no notification time set if the time is the default time.
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT user_id FROM users
                WHERE
                    (is_blocked = FALSE OR is_blocked IS NULL)
                    AND (
                        (notification_times ? $1)
                        OR
                        (
                            (notification_times IS NULL OR jsonb_array_length(notification_times) = 0)
                            AND $2 = $1
                        )
                    )
            """
            rows = await conn.fetch(
                query,
                notification_time.strftime("%H:%M"),
                default_notification_time.strftime("%H:%M"),
            )
            return [row["user_id"] for row in rows]

    async def get_todays_notification_count(self, user_id: int, notification_type: str) -> int:
        """Get the number of notifications of a specific type sent to a user today."""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM notifications
                WHERE user_id = $1 AND notification_type = $2 AND sent_at >= current_date
                """,
                user_id,
                notification_type,
            )
            return count or 0

    async def has_sent_notification_for_hour(self, user_id: int, notification_type: str, hour: int) -> bool:
        """Check if a notification has already been sent for the current hour."""
        async with self.pool.acquire() as conn:
            return (
                    await conn.fetchval(
                        """
                    SELECT 1 FROM notifications
                    WHERE user_id = $1
                      AND notification_type = $2
                      AND DATE(sent_at AT TIME ZONE 'utc') = DATE(NOW() AT TIME ZONE 'utc')
                      AND EXTRACT(HOUR FROM sent_at AT TIME ZONE 'utc') = $3
                    LIMIT 1;
                    """,
                        user_id,
                        notification_type,
                        hour,
                    )
                    is not None
            )

    async def log_notification(self, user_id: int, notification_type: str, message_id: int = None) -> int:
        """Log a sent notification and return its ID."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                """
                INSERT INTO notifications (user_id, notification_type, message_id)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                user_id,
                notification_type,
                message_id,
            )

    async def get_and_delete_inactivity_notification(self, user_id: int) -> Optional[int]:
        """Get and delete the last inactivity notification for a user."""
        async with self.pool.acquire() as conn:
            notification = await conn.fetchrow(
                """
                DELETE FROM notifications
                WHERE user_id = $1 AND notification_type = 'budge_inactive'
                RETURNING message_id
                """,
                user_id,
            )
            return notification["message_id"] if notification else None

    async def mark_notification_as_responded(self, notification_id: int) -> None:
        """Mark a notification as responded to."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE notifications
                SET is_responded_to = TRUE, responded_at = NOW()
                WHERE id = $1 AND is_responded_to = FALSE
                """,
                notification_id,
            )

    async def mark_notification_as_replaced(self, notification_id: int) -> None:
        """Mark a notification as replaced (not responded, but superseded by a new one)."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE notifications
                SET is_responded_to = FALSE, responded_at = NOW()
                WHERE id = $1 AND is_responded_to = FALSE
                """,
                notification_id,
            )

    async def delete_old_due_word_notifications(self, interval_hours: int = 72) -> int:
        """Delete due word notifications older than the specified interval in hours."""
        async with self.pool.acquire() as conn:
            # The result from conn.execute for DELETE is a string like 'DELETE 5'
            # We need to parse this string to get the number of deleted rows.
            result_str = await conn.execute(
                f"""
                DELETE FROM due_word_notifications
                WHERE created_at < NOW() - INTERVAL '{interval_hours} hours'
                """
            )
            try:
                # Assuming the format is "DELETE {count}"
                deleted_count = int(result_str.split(" ")[1])
            except (IndexError, ValueError):
                # If the format is unexpected or there's no count, return 0
                deleted_count = 0
            return deleted_count

    async def get_unanswered_review_notification(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent unanswered review notification for a user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT n.id as notification_id, n.message_id, dwn.id as due_word_id, dwn.word_ids
                FROM notifications n
                JOIN due_word_notifications dwn ON dwn.user_id = n.user_id 
                    AND dwn.created_at >= n.sent_at - INTERVAL '1 minute'
                    AND dwn.created_at <= n.sent_at + INTERVAL '1 minute'
                WHERE n.user_id = $1
                    AND n.notification_type = 'word_review'
                    AND n.is_responded_to = FALSE
                    AND n.responded_at IS NULL  -- Exclude replaced notifications
                    AND n.sent_at >= NOW() - INTERVAL '72 hours'
                ORDER BY n.sent_at DESC
                LIMIT 1
                """,
                user_id,
            )
            if row:
                return {
                    "notification_id": row["notification_id"],
                    "message_id": row["message_id"],
                    "due_word_id": row["due_word_id"],
                    "word_ids": json.loads(row["word_ids"]),
                }
            return None

    async def update_notification_message_id(self, notification_id: int, message_id: int) -> None:
        """Update the message_id for a notification."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE notifications
                SET message_id = $2
                WHERE id = $1
                """,
                notification_id,
                message_id,
            )
