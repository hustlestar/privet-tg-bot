"""Service for handling pronunciation with caching to reduce TTS API costs."""

import logging
import base64
from typing import Optional, Tuple
from datetime import datetime

from privet_api.services.audio.audio_service import AudioService
from privet_api.repositories.pronunciation_repository import PronunciationRepository

logger = logging.getLogger(__name__)


class PronunciationService:
    """Manages pronunciation generation and caching."""

    def __init__(
        self,
        audio_service: AudioService,
        pronunciation_repo: PronunciationRepository,
        default_voice_map: Optional[dict] = None,
    ):
        """Initialize PronunciationService.

        Args:
            audio_service: AudioService instance for TTS
            pronunciation_repo: PronunciationRepository for caching
            default_voice_map: Dict mapping language codes to default voices
                              e.g., {"en": "nova", "es": "alloy", "ru": "echo"}
        """
        self.audio_service = audio_service
        self.pronunciation_repo = pronunciation_repo
        self.default_voice_map = default_voice_map or {
            "en": "nova",
            "es": "alloy",
            "ru": "echo",
        }

    def _normalize_word(self, word: str) -> str:
        """Normalize word for cache lookup (lowercase, strip whitespace)."""
        return word.lower().strip()

    def _get_voice_for_language(self, language_code: str, voice_override: Optional[str] = None) -> str:
        """Get the appropriate voice for a language.

        Args:
            language_code: Language code (en, es, ru)
            voice_override: Optional voice override

        Returns:
            Voice ID to use
        """
        if voice_override:
            return voice_override

        return self.default_voice_map.get(language_code, "nova")

    async def get_pronunciation(
        self,
        text: str,
        language_code: str,
        voice_id: Optional[str] = None,
        use_cache: bool = True,
    ) -> Tuple[Optional[bytes], bool, Optional[int]]:
        """Get pronunciation audio for text, using cache if available.

        Args:
            text: Text to pronounce
            language_code: Language code (en, es, ru)
            voice_id: Optional voice ID override
            use_cache: Whether to use cache (default True)

        Returns:
            Tuple of (audio_bytes, from_cache, cache_id)
            - audio_bytes: The audio data or None if error
            - from_cache: Whether the audio was retrieved from cache
            - cache_id: Cache entry ID if cached, None otherwise
        """
        normalized = self._normalize_word(text)
        voice = self._get_voice_for_language(language_code, voice_id)

        # Try to get from cache first
        if use_cache:
            cached = await self.pronunciation_repo.get_cached_pronunciation(
                normalized_form=normalized,
                language_code=language_code,
                voice_id=voice,
            )

            if cached:
                logger.info(f"Cache hit for '{text}' ({language_code}, {voice})")
                try:
                    audio_bytes = base64.b64decode(cached['audio_data'])
                    return audio_bytes, True, cached['id']
                except Exception as e:
                    logger.error(f"Error decoding cached audio: {e}")
                    # Fall through to generate new audio

        # Cache miss or cache disabled - generate new audio
        logger.info(f"Cache miss for '{text}' ({language_code}, {voice}) - generating new audio")

        audio_bytes = await self.audio_service.text_to_speech(
            text=text,
            voice=voice,
        )

        if not audio_bytes:
            logger.error(f"Failed to generate audio for '{text}'")
            return None, False, None

        # Cache the generated audio
        if use_cache:
            try:
                audio_data_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                file_size = len(audio_bytes)

                cache_entry = await self.pronunciation_repo.create_cache_entry(
                    word_text=text,
                    normalized_form=normalized,
                    language_code=language_code,
                    voice_id=voice,
                    provider=self.audio_service.tts_provider_name,
                    audio_format="mp3",  # Default format from OpenAI TTS
                    audio_data=audio_data_b64,
                    file_size_bytes=file_size,
                )

                if cache_entry:
                    logger.info(f"Cached pronunciation for '{text}' (ID: {cache_entry['id']})")
                    return audio_bytes, False, cache_entry['id']
                else:
                    logger.warning(f"Failed to cache pronunciation for '{text}'")

            except Exception as e:
                logger.error(f"Error caching pronunciation: {e}", exc_info=True)

        return audio_bytes, False, None

    async def get_pronunciation_base64(
        self,
        text: str,
        language_code: str,
        voice_id: Optional[str] = None,
        use_cache: bool = True,
    ) -> Tuple[Optional[str], bool, Optional[int]]:
        """Get pronunciation as base64 string.

        Args:
            text: Text to pronounce
            language_code: Language code
            voice_id: Optional voice ID override
            use_cache: Whether to use cache

        Returns:
            Tuple of (base64_audio, from_cache, cache_id)
        """
        audio_bytes, from_cache, cache_id = await self.get_pronunciation(
            text=text,
            language_code=language_code,
            voice_id=voice_id,
            use_cache=use_cache,
        )

        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            return audio_b64, from_cache, cache_id

        return None, False, None

    async def bulk_cache_words(
        self,
        words: list[str],
        language_code: str,
        voice_id: Optional[str] = None,
    ) -> dict:
        """Pre-cache pronunciation for multiple words.

        Useful for caching common vocabulary in advance.

        Args:
            words: List of words to cache
            language_code: Language code
            voice_id: Optional voice ID override

        Returns:
            Dict with stats: {"cached": count, "skipped": count, "failed": count}
        """
        stats = {"cached": 0, "skipped": 0, "failed": 0}

        for word in words:
            normalized = self._normalize_word(word)
            voice = self._get_voice_for_language(language_code, voice_id)

            # Check if already cached
            cached = await self.pronunciation_repo.get_cached_pronunciation(
                normalized_form=normalized,
                language_code=language_code,
                voice_id=voice,
            )

            if cached:
                stats["skipped"] += 1
                continue

            # Generate and cache
            _, _, cache_id = await self.get_pronunciation(
                text=word,
                language_code=language_code,
                voice_id=voice_id,
                use_cache=True,
            )

            if cache_id:
                stats["cached"] += 1
            else:
                stats["failed"] += 1

        logger.info(f"Bulk cache completed: {stats}")
        return stats

    async def get_cache_stats(self, language_code: Optional[str] = None) -> dict:
        """Get pronunciation cache statistics.

        Args:
            language_code: Optional language filter

        Returns:
            Dict with cache stats
        """
        stats = await self.pronunciation_repo.get_cache_stats(language_code)

        if not stats:
            return {
                "total_entries": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
                "total_usage": 0,
                "language_code": language_code,
            }

        return {
            "total_entries": stats['total_entries'] or 0,
            "total_size_bytes": stats['total_size_bytes'] or 0,
            "total_size_mb": round((stats['total_size_bytes'] or 0) / (1024 * 1024), 2),
            "total_usage": stats['total_usage'] or 0,
            "language_code": stats.get('language_code', language_code),
        }

    async def cleanup_old_cache(self, days: int = 90) -> int:
        """Clean up old, rarely used cache entries.

        Args:
            days: Delete entries not used in this many days

        Returns:
            Number of entries deleted
        """
        count = await self.pronunciation_repo.cleanup_old_cache(days)
        logger.info(f"Cleaned up {count} old cache entries (>{days} days, usage_count=1)")
        return count
