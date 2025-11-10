"""Service for handling vocabulary management and word learning."""

import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from privet_api.repositories.vocabulary_repository import VocabularyRepository
from privet_api.repositories.pronunciation_repository import PronunciationRepository
from privet_api.services.pronunciation.pronunciation_service import PronunciationService

logger = logging.getLogger(__name__)


class VocabularyService:
    """Manages vocabulary words, extraction, and learning progress."""

    def __init__(
        self,
        vocabulary_repo: VocabularyRepository,
        pronunciation_service: PronunciationService,
    ):
        """Initialize VocabularyService.

        Args:
            vocabulary_repo: VocabularyRepository for word data
            pronunciation_service: PronunciationService for pronunciation caching
        """
        self.vocabulary_repo = vocabulary_repo
        self.pronunciation_service = pronunciation_service

    def _normalize_word(self, word: str) -> str:
        """Normalize word for consistent storage and matching."""
        return word.lower().strip()

    def _extract_words_from_text(self, text: str, language_code: str) -> List[str]:
        """Extract individual words from text.

        Args:
            text: Text to extract words from
            language_code: Language code for language-specific processing

        Returns:
            List of unique words
        """
        # Remove punctuation and split
        # This is a simple implementation - could be enhanced with spaCy for better tokenization
        words = re.findall(r'\b[\w\'-]+\b', text.lower())

        # Filter out very short words and numbers
        filtered = [w for w in words if len(w) > 2 and not w.isdigit()]

        # Return unique words preserving order
        seen = set()
        unique_words = []
        for word in filtered:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)

        return unique_words

    async def _get_translation_stub(
        self, word: str, source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Get translation for a word (STUB - will be replaced with external API).

        Args:
            word: Word to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Dict with translation data
        """
        # This is a stub that returns placeholder data
        # In production, this will call the external translation API
        return {
            "word": word,
            "translation": f"[Translation of '{word}' to {target_lang}]",
            "part_of_speech": "unknown",
            "difficulty_level": "B1",
            "example": f"Example sentence with '{word}'",
            "example_translation": f"Translated example",
            "is_stub": True,
        }

    async def extract_words_from_text(
        self,
        text: str,
        target_language: str,
        native_language: str,
        user_id: Optional[int] = None,
        max_words: int = 10,
    ) -> List[Dict[str, Any]]:
        """Extract interesting words from text with translations.

        Args:
            text: Text to analyze
            target_language: Language of the text
            native_language: User's native language for translation
            user_id: Optional user ID to check known words
            max_words: Maximum number of words to return

        Returns:
            List of dicts with word data
        """
        words = self._extract_words_from_text(text, target_language)[:max_words]

        extracted = []
        for word in words:
            normalized = self._normalize_word(word)

            # Check if user already knows this word
            is_known = False
            if user_id:
                is_known = await self.vocabulary_repo.check_word_exists(
                    user_id=user_id,
                    normalized_form=normalized,
                    target_language=target_language,
                )

            # Get translation (using stub for now)
            translation_data = await self._get_translation_stub(
                word=word,
                source_lang=target_language,
                target_lang=native_language,
            )

            extracted.append({
                "word": word,
                "translation": translation_data["translation"],
                "part_of_speech": translation_data.get("part_of_speech"),
                "difficulty_level": translation_data.get("difficulty_level"),
                "context": f"From text: ...{text[:50]}...",
                "is_known": is_known,
            })

        return extracted

    async def add_word_to_vocabulary(
        self,
        user_id: int,
        word_text: str,
        target_language: str,
        native_language: str,
        translation: Optional[str] = None,
        part_of_speech: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        example_sentence: Optional[str] = None,
        example_translation: Optional[str] = None,
        added_from_message_id: Optional[int] = None,
        auto_cache_pronunciation: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Add a word to user's vocabulary.

        Args:
            user_id: User ID
            word_text: The word to add
            target_language: Language of the word
            native_language: User's native language
            translation: Optional translation
            part_of_speech: Optional POS tag
            difficulty_level: Optional difficulty (A1-C2)
            example_sentence: Optional example
            example_translation: Optional example translation
            added_from_message_id: Optional message ID
            auto_cache_pronunciation: Whether to automatically cache pronunciation

        Returns:
            Created word record dict or None
        """
        normalized = self._normalize_word(word_text)

        # Check if word already exists
        exists = await self.vocabulary_repo.check_word_exists(
            user_id=user_id,
            normalized_form=normalized,
            target_language=target_language,
        )

        if exists:
            logger.info(f"Word '{word_text}' already exists for user {user_id}")
            return None

        # If no translation provided, get it from stub
        if not translation:
            translation_data = await self._get_translation_stub(
                word=word_text,
                source_lang=target_language,
                target_lang=native_language,
            )
            translation = translation_data["translation"]
            part_of_speech = part_of_speech or translation_data.get("part_of_speech")
            difficulty_level = difficulty_level or translation_data.get("difficulty_level")

        # Auto-cache pronunciation if enabled
        pronunciation_cache_id = None
        if auto_cache_pronunciation:
            try:
                _, from_cache, cache_id = await self.pronunciation_service.get_pronunciation(
                    text=word_text,
                    language_code=target_language,
                    use_cache=True,
                )
                pronunciation_cache_id = cache_id
                logger.info(f"Pronunciation cached for '{word_text}' (cache_id: {cache_id}, from_cache: {from_cache})")
            except Exception as e:
                logger.warning(f"Failed to cache pronunciation for '{word_text}': {e}")

        # Create word record
        word_record = await self.vocabulary_repo.create_word(
            user_id=user_id,
            word_text=word_text,
            normalized_form=normalized,
            target_language=target_language,
            native_language=native_language,
            translation=translation,
            part_of_speech=part_of_speech,
            difficulty_level=difficulty_level,
            example_sentence=example_sentence,
            example_translation=example_translation,
            pronunciation_cache_id=pronunciation_cache_id,
            added_from_message_id=added_from_message_id,
        )

        if word_record:
            logger.info(f"Added word '{word_text}' to vocabulary for user {user_id}")
            return dict(word_record)

        return None

    async def get_user_vocabulary(
        self,
        user_id: int,
        target_language: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get user's vocabulary with pagination.

        Args:
            user_id: User ID
            target_language: Optional language filter
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            Dict with items, total, offset, limit
        """
        words = await self.vocabulary_repo.get_user_words(
            user_id=user_id,
            target_language=target_language,
            is_active=True,
            offset=offset,
            limit=limit,
        )

        total = await self.vocabulary_repo.count_user_words(
            user_id=user_id,
            target_language=target_language,
            is_active=True,
        )

        return {
            "items": [dict(w) for w in words],
            "total": total,
            "offset": offset,
            "limit": limit,
        }

    async def record_word_review(
        self,
        word_id: int,
        user_id: int,
        was_correct: bool,
        review_type: str = "flashcard",
    ) -> Optional[Dict[str, Any]]:
        """Record a word review and update spaced repetition schedule.

        Uses a simplified SM-2 algorithm for spaced repetition.

        Args:
            word_id: Vocabulary word ID
            user_id: User ID
            was_correct: Whether the review was correct
            review_type: Type of review (flashcard, quiz, etc.)

        Returns:
            Updated word record with next review date
        """
        # Calculate next review date using simplified SM-2 algorithm
        word = await self.vocabulary_repo.get_word_by_id(word_id, user_id)

        if not word:
            logger.warning(f"Word {word_id} not found for user {user_id}")
            return None

        # Simplified SM-2: interval multipliers based on mastery level
        # This is a basic implementation - can be enhanced
        current_mastery = word['mastery_level']
        times_reviewed = word['times_reviewed']

        if was_correct:
            # Increase interval: 1 day, 3 days, 7 days, 14 days, 30 days, 60 days
            interval_map = {
                0: 1,  # New word
                1: 3,
                2: 7,
                3: 14,
                4: 30,
                5: 60,
            }
            new_mastery = min(5, current_mastery + 1)
            interval_days = interval_map.get(new_mastery, 60)
        else:
            # Reset interval on incorrect review
            new_mastery = max(0, current_mastery - 1)
            interval_days = 1

        next_review_at = datetime.utcnow() + timedelta(days=interval_days)

        # Record the review
        updated_word = await self.vocabulary_repo.record_review(
            word_id=word_id,
            user_id=user_id,
            was_correct=was_correct,
            next_review_at=next_review_at,
        )

        if updated_word:
            # Calculate XP earned (simple formula)
            xp_earned = 10 if was_correct else 2
            if was_correct and new_mastery >= 4:
                xp_earned = 20  # Bonus for mastering

            return {
                "word_id": word_id,
                "new_mastery_level": updated_word['mastery_level'],
                "next_review_at": updated_word['next_review_at'],
                "xp_earned": xp_earned,
            }

        return None

    async def get_words_for_review(
        self, user_id: int, limit: int = 10, review_type: str = "due"
    ) -> Dict[str, Any]:
        """Get words that need review.

        Args:
            user_id: User ID
            limit: Maximum number of words
            review_type: Type of review (all, due, mastered, learning)

        Returns:
            Dict with words and stats
        """
        words = await self.vocabulary_repo.get_words_for_review(
            user_id=user_id,
            limit=limit,
            review_type=review_type,
        )

        stats = await self.vocabulary_repo.get_vocabulary_stats(user_id)

        return {
            "words": [dict(w) for w in words],
            "total_due": stats['due_for_review'] if stats else 0,
            "total_learning": stats['learning_words'] if stats else 0,
            "total_mastered": stats['mastered_words'] if stats else 0,
        }

    async def get_vocabulary_stats(self, user_id: int) -> Dict[str, Any]:
        """Get vocabulary statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dict with vocabulary statistics
        """
        stats = await self.vocabulary_repo.get_vocabulary_stats(user_id)

        if not stats:
            return {
                "total_words": 0,
                "mastered_words": 0,
                "learning_words": 0,
                "due_for_review": 0,
                "avg_mastery": 0.0,
            }

        return {
            "total_words": stats['total_words'] or 0,
            "mastered_words": stats['mastered_words'] or 0,
            "learning_words": stats['learning_words'] or 0,
            "due_for_review": stats['due_for_review'] or 0,
            "avg_mastery": float(stats['avg_mastery'] or 0.0),
        }

    async def get_advanced_translation_stub(
        self, word: str, source_language: str, target_language: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get advanced translation data (STUB for external API).

        This is a placeholder that will be replaced with actual API integration.

        Args:
            word: Word to translate
            source_language: Source language code
            target_language: Target language code
            context: Optional context for better translation

        Returns:
            Dict with advanced translation data
        """
        # STUB: Return placeholder data
        return {
            "word": word,
            "translations": [
                f"Translation 1 of '{word}'",
                f"Translation 2 of '{word}'",
                f"Translation 3 of '{word}'",
            ],
            "definitions": [
                f"Definition 1 in {target_language}",
                f"Definition 2 in {target_language}",
            ],
            "examples": [
                {
                    "sentence": f"Example sentence with '{word}' in {source_language}",
                    "translation": f"Translated example in {target_language}",
                },
                {
                    "sentence": f"Another example with '{word}'",
                    "translation": f"Another translated example",
                },
            ],
            "synonyms": ["synonym1", "synonym2", "synonym3"],
            "antonyms": ["antonym1", "antonym2"],
            "conjugations": None,  # For verbs
            "etymology": f"Origin of '{word}' (stub)",
            "usage_notes": f"Usage notes for '{word}' (stub)",
            "stub_message": "Advanced translation feature will be integrated with external API",
        }
