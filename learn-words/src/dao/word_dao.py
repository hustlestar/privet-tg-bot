import json
from typing import Optional, List, Dict, Any

from src.dao.models import TranslationData, Word


class WordDao:
    def __init__(self, pool):
        self.pool = pool

    async def get_word(
        self,
        word: str,
        from_lang: str,
        to_lang: str,
        native_language: Optional[str] = None,
    ) -> Optional[Word]:
        """Get word translation from cache.

        Args:
            word: The word to translate
            from_lang: Source language
            to_lang: Target language
            native_language: The language the user is learning (optional, defaults to to_lang)
        """
        # If native_language is not provided, use to_lang as default
        if native_language is None:
            native_language = to_lang

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM words
                WHERE word = $1 AND from_language = $2 AND to_language = $3 AND native_language = $4
                """,
                word.lower().strip(),
                from_lang.lower().strip(),
                to_lang.lower().strip(),
                native_language.lower().strip(),
            )
            if row:
                return Word(
                    id=row["id"],
                    word=row["word"],
                    from_language=row["from_language"],
                    to_language=row["to_language"],
                    short_translation=row["short_translation"],
                    medium_data=json.loads(row["medium_data"]),
                    long_data=json.loads(row["long_data"]),
                    synonyms_native=json.loads(row.get("synonyms_native", "[]")),
                    synonyms_learning=json.loads(row.get("synonyms_learning", "[]")),
                    word_type=row["word_type"],
                    created_at=row["created_at"],
                    native_language=row.get("native_language"),
                )
            return None

    async def get_word_by_id(self, word_id: int) -> Optional[Word]:
        """Get word by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM words
                WHERE id = $1
                """,
                word_id,
            )
            if row:
                return Word(
                    id=row["id"],
                    word=row["word"],
                    from_language=row["from_language"],
                    to_language=row["to_language"],
                    short_translation=row["short_translation"],
                    medium_data=json.loads(row["medium_data"]),
                    long_data=json.loads(row["long_data"]),
                    synonyms_native=json.loads(row.get("synonyms_native", "[]")),
                    synonyms_learning=json.loads(row.get("synonyms_learning", "[]")),
                    word_type=row["word_type"],
                    created_at=row["created_at"],
                    native_language=row.get("native_language"),
                )
            return None

    async def save_word(self, translation_data: TranslationData) -> int:
        """Save word translation to database and return word ID."""
        async with self.pool.acquire() as conn:
            # Get native_language from translation_data or default to to_language
            native_language = getattr(translation_data, "native_language", translation_data.to_language)

            word_id = await conn.fetchval(
                """
                INSERT INTO words (word, from_language, to_language, native_language, short_translation, medium_data, long_data, synonyms_native, synonyms_learning)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (word, from_language, to_language, native_language)
                DO UPDATE SET
                    short_translation = EXCLUDED.short_translation,
                    medium_data = EXCLUDED.medium_data,
                    long_data = EXCLUDED.long_data,
                    synonyms_native = EXCLUDED.synonyms_native,
                    synonyms_learning = EXCLUDED.synonyms_learning
                RETURNING id
                """,
                translation_data.word.lower().strip(),
                translation_data.from_language.lower().strip(),
                translation_data.to_language.lower().strip(),
                native_language.lower().strip(),
                translation_data.short,
                json.dumps(translation_data.medium),
                json.dumps(translation_data.long),
                json.dumps(getattr(translation_data, "synonyms_native", [])),
                json.dumps(getattr(translation_data, "synonyms_learning", [])),
            )
            return word_id

    # User vocabulary operations
    async def add_word_to_user_vocabulary(self, user_id: int, word_id: int) -> None:
        """Add word to user's vocabulary."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_word_stats (user_id, word_id, is_hidden)
                VALUES ($1, $2, FALSE)
                ON CONFLICT (user_id, word_id) DO UPDATE SET
                    is_hidden = FALSE
                """,
                user_id,
                word_id,
            )

    async def hide_word_for_user(self, user_id: int, word_id: int) -> bool:
        """Mark a word as hidden for a user."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE user_word_stats
                SET is_hidden = TRUE
                WHERE user_id = $1 AND word_id = $2
                """,
                user_id,
                word_id,
            )
            return result != "UPDATE 0"

    async def get_user_vocabulary_count(self, user_id: int) -> int:
        """Get count of words in user's vocabulary."""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM user_word_stats WHERE user_id = $1 AND is_hidden = FALSE",
                user_id,
            )
            return count or 0

    async def get_user_vocabulary_with_stats(self, user_id: int, limit: int = 20, offset: int = 0, sort_recent: bool = True) -> List[Dict[str, Any]]:
        """Get user's vocabulary with statistics for browsing."""
        async with self.pool.acquire() as conn:
            order_clause = "uws.added_at DESC" if sort_recent else "uws.added_at ASC"

            rows = await conn.fetch(
                f"""
                SELECT w.id, w.word, w.short_translation, uws.total_attempts, uws.correct_answers,
                       uws.added_at as date_added
                FROM words w
                JOIN user_word_stats uws ON w.id = uws.word_id
                WHERE uws.user_id = $1 AND uws.is_hidden = FALSE
                ORDER BY {order_clause}
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset,
            )

            return [
                {
                    "id": row["id"],
                    "word": row["word"],
                    "translation": row["short_translation"],
                    "total_attempts": row["total_attempts"],
                    "correct_answers": row["correct_answers"],
                    "date_added": row["date_added"],
                }
                for row in rows
            ]

    async def mark_word_as_known(
        self,
        user_id: int,
        word: str,
        from_lang: str,
        to_lang: str,
        native_language: Optional[str] = None,
    ) -> bool:
        """Mark a word as known by the user."""
        # If native_language is not provided, use to_lang as default
        if native_language is None:
            native_language = to_lang

        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE user_word_stats
                SET is_marked_known = TRUE
                FROM words w
                WHERE user_word_stats.word_id = w.id
                    AND user_word_stats.user_id = $1
                    AND w.word = $2
                    AND w.from_language = $3
                    AND w.to_language = $4
                    AND w.native_language = $5
                """,
                user_id,
                word.lower().strip(),
                from_lang.lower().strip(),
                to_lang.lower().strip(),
                native_language.lower().strip(),
            )
            return result != "UPDATE 0"

    async def mark_word_as_known_by_id(self, user_id: int, word_id: int) -> bool:
        """Mark a word as known by the user using word ID."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE user_word_stats 
                SET is_marked_known = TRUE, repetition_level = 5
                WHERE user_id = $1 AND word_id = $2
                """,
                user_id,
                word_id,
            )
            return result != "UPDATE 0"
