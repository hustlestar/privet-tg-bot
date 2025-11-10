"""Repository for vocabulary words operations."""

import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class VocabularyRepository(BaseRepository):
    """Repository for vocabulary words data access."""

    async def create_word(
        self,
        user_id: int,
        word_text: str,
        normalized_form: str,
        target_language: str,
        native_language: str,
        translation: Optional[str] = None,
        part_of_speech: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        example_sentence: Optional[str] = None,
        example_translation: Optional[str] = None,
        pronunciation_ipa: Optional[str] = None,
        pronunciation_cache_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        added_from_message_id: Optional[int] = None,
    ) -> Optional[asyncpg.Record]:
        """Create a new vocabulary word.

        Returns:
            The created word record or None
        """
        query = """
            INSERT INTO vocabulary_words (
                user_id, word_text, normalized_form, target_language, native_language,
                translation, part_of_speech, difficulty_level, example_sentence,
                example_translation, pronunciation_ipa, pronunciation_cache_id,
                metadata, added_from_message_id, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW(), NOW())
            RETURNING *
        """
        try:
            import json
            metadata_json = json.dumps(metadata) if metadata else None

            return await self.fetchrow(
                query,
                user_id,
                word_text,
                normalized_form,
                target_language,
                native_language,
                translation,
                part_of_speech,
                difficulty_level,
                example_sentence,
                example_translation,
                pronunciation_ipa,
                pronunciation_cache_id,
                metadata_json,
                added_from_message_id,
            )
        except Exception as e:
            logger.error(f"Error creating vocabulary word: {e}", exc_info=True)
            return None

    async def get_word_by_id(self, word_id: int, user_id: int) -> Optional[asyncpg.Record]:
        """Get a vocabulary word by ID for a specific user."""
        query = """
            SELECT * FROM vocabulary_words
            WHERE id = $1 AND user_id = $2
        """
        try:
            return await self.fetchrow(query, word_id, user_id)
        except Exception as e:
            logger.error(f"Error fetching word by ID: {e}", exc_info=True)
            return None

    async def check_word_exists(
        self, user_id: int, normalized_form: str, target_language: str
    ) -> bool:
        """Check if a word already exists for a user."""
        query = """
            SELECT EXISTS(
                SELECT 1 FROM vocabulary_words
                WHERE user_id = $1
                  AND normalized_form = $2
                  AND target_language = $3
                  AND is_active = TRUE
            )
        """
        try:
            return await self.fetchval(query, user_id, normalized_form, target_language)
        except Exception as e:
            logger.error(f"Error checking word exists: {e}", exc_info=True)
            return False

    async def get_user_words(
        self,
        user_id: int,
        target_language: Optional[str] = None,
        is_active: bool = True,
        offset: int = 0,
        limit: int = 20,
    ) -> List[asyncpg.Record]:
        """Get vocabulary words for a user with pagination."""
        conditions = ["user_id = $1", "is_active = $2"]
        params: List[Any] = [user_id, is_active]
        param_count = 2

        if target_language:
            param_count += 1
            conditions.append(f"target_language = ${param_count}")
            params.append(target_language)

        param_count += 1
        offset_param = f"${param_count}"
        params.append(offset)

        param_count += 1
        limit_param = f"${param_count}"
        params.append(limit)

        query = f"""
            SELECT * FROM vocabulary_words
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            OFFSET {offset_param} LIMIT {limit_param}
        """
        try:
            return await self.fetch(query, *params)
        except Exception as e:
            logger.error(f"Error fetching user words: {e}", exc_info=True)
            return []

    async def count_user_words(
        self, user_id: int, target_language: Optional[str] = None, is_active: bool = True
    ) -> int:
        """Count vocabulary words for a user."""
        conditions = ["user_id = $1", "is_active = $2"]
        params: List[Any] = [user_id, is_active]

        if target_language:
            conditions.append(f"target_language = $3")
            params.append(target_language)

        query = f"""
            SELECT COUNT(*) FROM vocabulary_words
            WHERE {' AND '.join(conditions)}
        """
        try:
            return await self.fetchval(query, *params) or 0
        except Exception as e:
            logger.error(f"Error counting user words: {e}", exc_info=True)
            return 0

    async def update_word(
        self,
        word_id: int,
        user_id: int,
        **fields,
    ) -> Optional[asyncpg.Record]:
        """Update a vocabulary word."""
        if not fields:
            return await self.get_word_by_id(word_id, user_id)

        # Build SET clause dynamically
        set_clauses = []
        params = []
        param_count = 1

        for field, value in fields.items():
            if value is not None:
                set_clauses.append(f"{field} = ${param_count}")
                params.append(value)
                param_count += 1

        if not set_clauses:
            return await self.get_word_by_id(word_id, user_id)

        set_clauses.append(f"updated_at = ${param_count}")
        params.append(datetime.utcnow())
        param_count += 1

        params.extend([word_id, user_id])

        query = f"""
            UPDATE vocabulary_words
            SET {', '.join(set_clauses)}
            WHERE id = ${param_count} AND user_id = ${param_count + 1}
            RETURNING *
        """
        try:
            return await self.fetchrow(query, *params)
        except Exception as e:
            logger.error(f"Error updating word: {e}", exc_info=True)
            return None

    async def delete_word(self, word_id: int, user_id: int) -> bool:
        """Delete a vocabulary word (soft delete by setting is_active=False)."""
        query = """
            UPDATE vocabulary_words
            SET is_active = FALSE, updated_at = NOW()
            WHERE id = $1 AND user_id = $2
        """
        try:
            result = await self.execute(query, word_id, user_id)
            return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Error deleting word: {e}", exc_info=True)
            return False

    async def record_review(
        self, word_id: int, user_id: int, was_correct: bool, next_review_at: Optional[datetime] = None
    ) -> Optional[asyncpg.Record]:
        """Record a word review and update mastery level."""
        query = """
            UPDATE vocabulary_words
            SET times_reviewed = times_reviewed + 1,
                times_correct = times_correct + CASE WHEN $3 THEN 1 ELSE 0 END,
                mastery_level = LEAST(5, GREATEST(0, mastery_level + CASE WHEN $3 THEN 1 ELSE -1 END)),
                last_reviewed_at = NOW(),
                next_review_at = $4,
                updated_at = NOW()
            WHERE id = $1 AND user_id = $2
            RETURNING *
        """
        try:
            return await self.fetchrow(query, word_id, user_id, was_correct, next_review_at)
        except Exception as e:
            logger.error(f"Error recording review: {e}", exc_info=True)
            return None

    async def get_words_for_review(
        self, user_id: int, limit: int = 10, review_type: str = "due"
    ) -> List[asyncpg.Record]:
        """Get words for review based on spaced repetition schedule.

        Args:
            user_id: User ID
            limit: Maximum number of words
            review_type: Type of review (all, due, mastered, learning)
        """
        base_query = """
            SELECT * FROM vocabulary_words
            WHERE user_id = $1 AND is_active = TRUE
        """

        if review_type == "due":
            base_query += " AND (next_review_at IS NULL OR next_review_at <= NOW())"
        elif review_type == "mastered":
            base_query += " AND mastery_level >= 4"
        elif review_type == "learning":
            base_query += " AND mastery_level < 4"

        query = f"{base_query} ORDER BY next_review_at ASC NULLS FIRST LIMIT $2"

        try:
            return await self.fetch(query, user_id, limit)
        except Exception as e:
            logger.error(f"Error fetching words for review: {e}", exc_info=True)
            return []

    async def get_vocabulary_stats(self, user_id: int) -> Optional[asyncpg.Record]:
        """Get vocabulary statistics for a user."""
        query = """
            SELECT
                COUNT(*) as total_words,
                COUNT(*) FILTER (WHERE mastery_level >= 4) as mastered_words,
                COUNT(*) FILTER (WHERE mastery_level < 4) as learning_words,
                COUNT(*) FILTER (WHERE next_review_at IS NOT NULL AND next_review_at <= NOW()) as due_for_review,
                AVG(mastery_level) as avg_mastery
            FROM vocabulary_words
            WHERE user_id = $1 AND is_active = TRUE
        """
        try:
            return await self.fetchrow(query, user_id)
        except Exception as e:
            logger.error(f"Error fetching vocabulary stats: {e}", exc_info=True)
            return None
