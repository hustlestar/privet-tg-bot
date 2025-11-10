"""Repository for pronunciation cache operations."""

import asyncpg
from typing import Optional, List
from datetime import datetime
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class PronunciationRepository(BaseRepository):
    """Repository for pronunciation cache data access."""

    async def create_cache_entry(
        self,
        word_text: str,
        normalized_form: str,
        language_code: str,
        voice_id: str,
        provider: str,
        audio_format: str,
        audio_data: str,
        file_size_bytes: int,
        duration_seconds: Optional[int] = None,
        sample_rate: Optional[int] = None,
        ipa_pronunciation: Optional[str] = None,
    ) -> Optional[asyncpg.Record]:
        """Create a new pronunciation cache entry.

        Args:
            word_text: The word or phrase
            normalized_form: Lowercase normalized form
            language_code: Language code (es, en, ru)
            voice_id: TTS voice identifier
            provider: TTS provider (openai, elevenlabs, google)
            audio_format: Audio file format (mp3, wav, etc.)
            audio_data: Base64 encoded audio data
            file_size_bytes: Size of decoded audio
            duration_seconds: Audio duration (optional)
            sample_rate: Audio sample rate (optional)
            ipa_pronunciation: IPA phonetic notation (optional)

        Returns:
            The created cache entry record or None
        """
        query = """
            INSERT INTO pronunciation_cache (
                word_text, normalized_form, language_code, voice_id, provider,
                audio_format, audio_data, file_size_bytes, duration_seconds,
                sample_rate, ipa_pronunciation, usage_count, created_at, last_used_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 1, NOW(), NOW())
            ON CONFLICT (normalized_form, language_code, voice_id)
            DO UPDATE SET
                usage_count = pronunciation_cache.usage_count + 1,
                last_used_at = NOW()
            RETURNING *
        """
        try:
            return await self.fetchrow(
                query,
                word_text,
                normalized_form,
                language_code,
                voice_id,
                provider,
                audio_format,
                audio_data,
                file_size_bytes,
                duration_seconds,
                sample_rate,
                ipa_pronunciation,
            )
        except Exception as e:
            logger.error(f"Error creating cache entry: {e}", exc_info=True)
            return None

    async def get_cached_pronunciation(
        self,
        normalized_form: str,
        language_code: str,
        voice_id: str,
    ) -> Optional[asyncpg.Record]:
        """Get cached pronunciation if available.

        Args:
            normalized_form: Lowercase normalized form
            language_code: Language code
            voice_id: TTS voice identifier

        Returns:
            Cached pronunciation record or None
        """
        query = """
            SELECT * FROM pronunciation_cache
            WHERE normalized_form = $1
              AND language_code = $2
              AND voice_id = $3
            LIMIT 1
        """
        try:
            cache_entry = await self.fetchrow(query, normalized_form, language_code, voice_id)

            if cache_entry:
                # Update usage count and last_used_at
                await self.increment_usage(cache_entry['id'])

            return cache_entry
        except Exception as e:
            logger.error(f"Error fetching cached pronunciation: {e}", exc_info=True)
            return None

    async def increment_usage(self, cache_id: int) -> None:
        """Increment usage count for a cache entry.

        Args:
            cache_id: Cache entry ID
        """
        query = """
            UPDATE pronunciation_cache
            SET usage_count = usage_count + 1,
                last_used_at = NOW()
            WHERE id = $1
        """
        try:
            await self.execute(query, cache_id)
        except Exception as e:
            logger.error(f"Error incrementing cache usage: {e}", exc_info=True)

    async def get_by_id(self, cache_id: int) -> Optional[asyncpg.Record]:
        """Get pronunciation cache entry by ID.

        Args:
            cache_id: Cache entry ID

        Returns:
            Cache entry record or None
        """
        query = """
            SELECT * FROM pronunciation_cache
            WHERE id = $1
        """
        try:
            return await self.fetchrow(query, cache_id)
        except Exception as e:
            logger.error(f"Error fetching cache entry by ID: {e}", exc_info=True)
            return None

    async def get_cache_stats(self, language_code: Optional[str] = None) -> Optional[asyncpg.Record]:
        """Get cache statistics.

        Args:
            language_code: Optional language filter

        Returns:
            Statistics record with total_entries, total_size_bytes, total_usage
        """
        if language_code:
            query = """
                SELECT
                    COUNT(*) as total_entries,
                    SUM(file_size_bytes) as total_size_bytes,
                    SUM(usage_count) as total_usage,
                    language_code
                FROM pronunciation_cache
                WHERE language_code = $1
                GROUP BY language_code
            """
            return await self.fetchrow(query, language_code)
        else:
            query = """
                SELECT
                    COUNT(*) as total_entries,
                    SUM(file_size_bytes) as total_size_bytes,
                    SUM(usage_count) as total_usage
                FROM pronunciation_cache
            """
            return await self.fetchrow(query)

    async def delete_cache_entry(self, cache_id: int) -> bool:
        """Delete a cache entry.

        Args:
            cache_id: Cache entry ID

        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM pronunciation_cache WHERE id = $1"
        try:
            result = await self.execute(query, cache_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}", exc_info=True)
            return False

    async def cleanup_old_cache(self, days: int = 90) -> int:
        """Delete cache entries older than specified days that haven't been used recently.

        Args:
            days: Number of days threshold

        Returns:
            Number of entries deleted
        """
        query = """
            DELETE FROM pronunciation_cache
            WHERE last_used_at < NOW() - INTERVAL '%s days'
              AND usage_count = 1
            RETURNING id
        """
        try:
            deleted = await self.fetch(query.replace('%s', str(days)))
            count = len(deleted)
            logger.info(f"Cleaned up {count} old cache entries")
            return count
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}", exc_info=True)
            return 0
