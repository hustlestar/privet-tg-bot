import json
import logging
import random
from typing import Optional, List, Tuple

from src.dao.models import Word, UserWordStats, TrainingAttempt
from src.repetition import get_next_review_date
from src.utils import async_timer

logger = logging.getLogger(__name__)


class TrainingDao:
    def __init__(self, pool):
        self.pool = pool

    # Training operations
    @async_timer
    async def get_word_for_training(self, user_id: int) -> Optional[Tuple[Word, UserWordStats]]:
        """Get a word for training based on a priority algorithm executed in the database."""
        async with self.pool.acquire() as conn:
            # This query calculates a priority score in the database to select the best words.
            rows = await conn.fetch(
                """
                WITH word_priorities AS (
                    SELECT
                        w.*,
                        uws.total_attempts, uws.correct_answers,
                        uws.last_seen, uws.is_marked_known, uws.added_at, uws.is_hidden,
                        uws.repetition_level, uws.next_review_at,
                        (
                            (1 - (CASE WHEN uws.total_attempts > 0 THEN uws.correct_answers::FLOAT / uws.total_attempts ELSE 0 END)) * 100 +  -- Success penalty
                            GREATEST(0, (10 - uws.total_attempts)) * 10 +  -- Trial penalty
                            CASE
                                WHEN uws.last_seen IS NOT NULL THEN
                                    LEAST(EXTRACT(DAY FROM (NOW() - uws.last_seen)) * 5, 50)
                                ELSE 100  -- Time bonus for new words
                            END +
                            CASE WHEN uws.is_marked_known THEN -30 ELSE 0 END  -- Known penalty
                        ) AS priority_score
                    FROM words w
                    JOIN user_word_stats uws ON w.id = uws.word_id
                    WHERE uws.user_id = $1 AND uws.is_hidden = FALSE
                )
                SELECT *
                FROM word_priorities
                ORDER BY priority_score DESC, RANDOM()
                LIMIT 3
                """,
                user_id,
            )

            if not rows:
                return None

            # Randomly select one of the top candidates
            selected_row = random.choice(rows)

            stats = UserWordStats(
                user_id=user_id,
                word_id=selected_row["id"],
                total_attempts=selected_row["total_attempts"],
                correct_answers=selected_row["correct_answers"],
                last_seen=selected_row["last_seen"],
                is_marked_known=selected_row["is_marked_known"],
                is_hidden=selected_row["is_hidden"],
                added_at=selected_row["added_at"],
                repetition_level=selected_row.get("repetition_level", 0),
                next_review_at=selected_row.get("next_review_at"),
            )

            word = Word(
                id=selected_row["id"],
                word=selected_row["word"],
                from_language=selected_row["from_language"],
                to_language=selected_row["to_language"],
                short_translation=selected_row["short_translation"],
                medium_data=json.loads(selected_row["medium_data"]),
                long_data=json.loads(selected_row["long_data"]),
                word_type=selected_row["word_type"],
                created_at=selected_row["created_at"],
                native_language=selected_row.get("native_language"),
                synonyms_native=json.loads(selected_row.get("synonyms_native"))
                if selected_row.get("synonyms_native")
                else [],
                synonyms_learning=json.loads(selected_row.get("synonyms_learning"))
                if selected_row.get("synonyms_learning")
                else [],
            )

            return word, stats

    async def get_words_by_ids_for_user(self, user_id: int, word_ids: List[int]) -> List[Tuple[Word, UserWordStats]]:
        """Get a list of words and their stats for a user by word IDs."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT w.*, uws.total_attempts, uws.correct_answers,
                       uws.last_seen, uws.is_marked_known, uws.added_at, uws.is_hidden,
                       uws.repetition_level, uws.next_review_at
                FROM words w
                JOIN user_word_stats uws ON w.id = uws.word_id
                WHERE uws.user_id = $1 AND uws.word_id = ANY($2::int[])
                """,
                user_id,
                word_ids,
            )

            results = []
            for row in rows:
                stats = UserWordStats(
                    user_id=user_id,
                    word_id=row["id"],
                    total_attempts=row["total_attempts"],
                    correct_answers=row["correct_answers"],
                    last_seen=row["last_seen"],
                    is_marked_known=row["is_marked_known"],
                    is_hidden=row["is_hidden"],
                    added_at=row["added_at"],
                    repetition_level=row.get("repetition_level", 0),
                    next_review_at=row.get("next_review_at"),
                )
                word = Word(
                    id=row["id"],
                    word=row["word"],
                    from_language=row["from_language"],
                    to_language=row["to_language"],
                    short_translation=row["short_translation"],
                    medium_data=json.loads(row["medium_data"]),
                    long_data=json.loads(row["long_data"]),
                    word_type=row["word_type"],
                    created_at=row["created_at"],
                    native_language=row.get("native_language"),
                    synonyms_native=json.loads(row.get("synonyms_native")) if row.get("synonyms_native") else [],
                    synonyms_learning=json.loads(row.get("synonyms_learning")) if row.get("synonyms_learning") else [],
                )
                results.append((word, stats))
            return results

    async def get_word_by_id_for_user(self, user_id: int, word_id: int) -> Optional[Tuple[Word, UserWordStats]]:
        """Get a single word and its stats for a user by word ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT w.*, uws.total_attempts, uws.correct_answers,
                       uws.last_seen, uws.is_marked_known, uws.added_at, uws.is_hidden,
                       uws.repetition_level, uws.next_review_at
                FROM words w
                JOIN user_word_stats uws ON w.id = uws.word_id
                WHERE uws.user_id = $1 AND uws.word_id = $2
                """,
                user_id,
                word_id,
            )

            if not row:
                return None

            stats = UserWordStats(
                user_id=user_id,
                word_id=row["id"],
                total_attempts=row["total_attempts"],
                correct_answers=row["correct_answers"],
                last_seen=row["last_seen"],
                is_marked_known=row["is_marked_known"],
                is_hidden=row["is_hidden"],
                added_at=row["added_at"],
                repetition_level=row.get("repetition_level", 0),
                next_review_at=row.get("next_review_at"),
            )
            word = Word(
                id=row["id"],
                word=row["word"],
                from_language=row["from_language"],
                to_language=row["to_language"],
                short_translation=row["short_translation"],
                medium_data=json.loads(row["medium_data"]),
                long_data=json.loads(row["long_data"]),
                word_type=row["word_type"],
                created_at=row["created_at"],
                native_language=row.get("native_language"),
                synonyms_native=json.loads(row.get("synonyms_native")) if row.get("synonyms_native") else [],
                synonyms_learning=json.loads(row.get("synonyms_learning")) if row.get("synonyms_learning") else [],
            )
            return word, stats

    @async_timer
    async def get_random_translations_for_distractors(
        self, user_id: int, exclude_word_id: int, to_language: str, count: int = 3
    ) -> List[str]:
        """Get random short_translations for multiple choice distractors from the user's vocabulary."""
        async with self.pool.acquire() as conn:
            logger.debug(f"Fetching translation distractors for user {user_id}, excluding word {exclude_word_id}")
            rows = await conn.fetch(
                """
                SELECT w.short_translation
                FROM words w
                JOIN user_word_stats uws ON w.id = uws.word_id
                WHERE uws.user_id = $1 AND w.id != $2 AND uws.is_hidden = FALSE AND w.to_language = $3
                ORDER BY RANDOM()
                LIMIT $4
                """,
                user_id,
                exclude_word_id,
                to_language,
                count,
            )
            return [row["short_translation"] for row in rows]

    async def get_random_words_for_synonym_distractors(
        self,
        user_id: int,
        exclude_word_id: int,
        from_language: str,
        learning_language: str,
        count: int = 3,
        exclude_words: Optional[List[str]] = None,
    ) -> List[Word]:
        """Get random Word objects for synonym exercise distractors."""
        async with self.pool.acquire() as conn:
            query = "SELECT * FROM words WHERE from_language = $1 AND to_language = $2 AND id != $3"
            params = [from_language, learning_language, exclude_word_id]

            if exclude_words:
                placeholders = ", ".join(f"${i + 4}" for i in range(len(exclude_words)))
                query += f" AND word NOT IN ({placeholders})"
                params.extend(exclude_words)

            limit_pos = len(params) + 1
            query += f" ORDER BY RANDOM() LIMIT ${limit_pos}"
            params.append(count)

            logger.debug(f"Fetching synonym distractors with query: {query} and params: {params}")
            rows = await conn.fetch(query, *params)

            distractor_words = []
            for row in rows:
                distractor_words.append(
                    Word(
                        id=row["id"],
                        word=row["word"],
                        from_language=row["from_language"],
                        to_language=row["to_language"],
                        short_translation=row["short_translation"],
                        medium_data=json.loads(row["medium_data"]),
                        long_data=json.loads(row["long_data"]),
                        word_type=row["word_type"],
                        created_at=row["created_at"],
                        native_language=row.get("native_language"),
                        synonyms_native=json.loads(row.get("synonyms_native")) if row.get("synonyms_native") else [],
                        synonyms_learning=json.loads(row.get("synonyms_learning"))
                        if row.get("synonyms_learning")
                        else [],
                    )
                )
            return distractor_words

    async def record_training_attempt(self, attempt: TrainingAttempt, is_review_session: bool = False) -> int:
        """Record a training attempt and update user word stats. Returns attempt ID."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Record the attempt and get ID
                attempt_id = await conn.fetchval(
                    """
                    INSERT INTO training_attempts (user_id, word_id, training_type, is_correct)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    attempt.user_id,
                    attempt.word_id,
                    attempt.training_type.value,
                    attempt.is_correct,
                )

                # Get current repetition level
                stats = await conn.fetchrow(
                    "SELECT repetition_level FROM user_word_stats WHERE user_id = $1 AND word_id = $2",
                    attempt.user_id,
                    attempt.word_id,
                )
                current_level = stats["repetition_level"] if stats else 0

                # Calculate new repetition schedule
                new_level, next_review = get_next_review_date(current_level, attempt.is_correct, is_review_session)

                # Update user word stats
                await conn.execute(
                    """
                    UPDATE user_word_stats
                    SET total_attempts = total_attempts + 1,
                        correct_answers = correct_answers + $3,
                        last_seen = NOW(),
                        repetition_level = $4,
                        next_review_at = $5
                    WHERE user_id = $1 AND word_id = $2
                    """,
                    attempt.user_id,
                    attempt.word_id,
                    1 if attempt.is_correct else 0,
                    new_level,
                    next_review,
                )
                return attempt_id

    async def update_training_attempt_to_correct(self, attempt_id: int, previous_repetition_level: int) -> bool:
        """Update a training attempt to mark it as correct and restore repetition state."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Step 1: Update the attempt status
                result = await conn.execute(
                    """
                    UPDATE training_attempts
                    SET is_correct = TRUE
                    WHERE id = $1 AND is_correct = FALSE
                    """,
                    attempt_id,
                )

                if result == "UPDATE 0":
                    return False  # Attempt already correct or not found

                # Step 2: Get attempt details for stats update
                attempt_data = await conn.fetchrow(
                    "SELECT user_id, word_id FROM training_attempts WHERE id = $1",
                    attempt_id,
                )

                if not attempt_data:
                    return False

                user_id = attempt_data["user_id"]
                word_id = attempt_data["word_id"]

                # Step 3: Recalculate repetition schedule as if the answer was correct
                new_level, next_review = get_next_review_date(previous_repetition_level, is_correct=True)

                # Step 4: Update user word stats
                # - Increment correct_answers
                # - Restore repetition_level and next_review_at
                await conn.execute(
                    """
                    UPDATE user_word_stats
                    SET correct_answers = correct_answers + 1,
                        repetition_level = $3,
                        next_review_at = $4
                    WHERE user_id = $1 AND word_id = $2
                    """,
                    user_id,
                    word_id,
                    new_level,
                    next_review,
                )

                return True
