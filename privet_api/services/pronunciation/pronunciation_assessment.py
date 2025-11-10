"""Pronunciation assessment service for evaluating user pronunciation accuracy."""

import logging
from typing import Dict, Any, Optional
from difflib import SequenceMatcher
import re

logger = logging.getLogger(__name__)


class PronunciationAssessmentService:
    """Service for assessing pronunciation quality and providing feedback."""

    def __init__(self, audio_service):
        """
        Initialize pronunciation assessment service.

        Args:
            audio_service: AudioService instance for STT
        """
        self.audio_service = audio_service

    async def assess_pronunciation(
        self,
        audio_data: bytes,
        expected_text: str,
        language: str = "en",
        filename: str = "pronunciation.ogg"
    ) -> Dict[str, Any]:
        """
        Assess pronunciation quality by comparing spoken audio to expected text.

        Args:
            audio_data: User's pronunciation audio as bytes
            expected_text: The text the user was supposed to pronounce
            language: Language code (en, es, ru)
            filename: Audio filename for format detection

        Returns:
            Dict containing:
                - accuracy_score: 0-100 score
                - transcribed_text: What the user actually said
                - expected_text: What they should have said
                - is_correct: Boolean if pronunciation is acceptable
                - feedback: Specific feedback message
                - issues: List of specific pronunciation issues
        """
        try:
            # Transcribe the user's audio
            transcribed_text = await self.audio_service.transcribe_voice(
                voice_file=audio_data,
                filename=filename
            )

            if not transcribed_text:
                return {
                    "success": False,
                    "error": "Failed to transcribe audio"
                }

            # Normalize both texts for comparison
            expected_normalized = self._normalize_text(expected_text)
            transcribed_normalized = self._normalize_text(transcribed_text)

            # Calculate similarity score
            similarity = self._calculate_similarity(expected_normalized, transcribed_normalized)
            accuracy_score = int(similarity * 100)

            # Determine if pronunciation is acceptable (threshold: 80%)
            is_correct = accuracy_score >= 80

            # Generate specific feedback
            feedback, issues = self._generate_feedback(
                expected_normalized,
                transcribed_normalized,
                accuracy_score
            )

            return {
                "success": True,
                "accuracy_score": accuracy_score,
                "transcribed_text": transcribed_text,
                "expected_text": expected_text,
                "is_correct": is_correct,
                "feedback": feedback,
                "issues": issues,
                "language": language
            }

        except Exception as e:
            logger.error(f"Error assessing pronunciation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison by removing punctuation, converting to lowercase.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation except apostrophes (important for contractions)
        text = re.sub(r"[^\w\s']", "", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    def _calculate_similarity(self, expected: str, transcribed: str) -> float:
        """
        Calculate similarity between expected and transcribed text.

        Uses SequenceMatcher for fuzzy string matching.

        Args:
            expected: Expected normalized text
            transcribed: Transcribed normalized text

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        # Use difflib's SequenceMatcher for fuzzy matching
        matcher = SequenceMatcher(None, expected, transcribed)
        return matcher.ratio()

    def _generate_feedback(
        self,
        expected: str,
        transcribed: str,
        accuracy_score: int
    ) -> tuple[str, list[str]]:
        """
        Generate specific feedback based on comparison.

        Args:
            expected: Expected normalized text
            transcribed: Transcribed normalized text
            accuracy_score: Calculated accuracy score (0-100)

        Returns:
            Tuple of (feedback message, list of specific issues)
        """
        issues = []

        # Check for exact match
        if expected == transcribed:
            return "Perfect pronunciation! Great job!", []

        # High accuracy
        if accuracy_score >= 90:
            feedback = "Excellent pronunciation! Very close to perfect."
            issues.append("Minor differences detected, but overall very good")
        # Good accuracy
        elif accuracy_score >= 80:
            feedback = "Good pronunciation! A few small improvements needed."
            issues = self._identify_differences(expected, transcribed)
        # Moderate accuracy
        elif accuracy_score >= 60:
            feedback = "Fair pronunciation. Keep practicing!"
            issues = self._identify_differences(expected, transcribed)
        # Low accuracy
        else:
            feedback = "Pronunciation needs improvement. Try speaking more slowly and clearly."
            issues = self._identify_differences(expected, transcribed)
            issues.append("Consider listening to the reference pronunciation again")

        return feedback, issues

    def _identify_differences(self, expected: str, transcribed: str) -> list[str]:
        """
        Identify specific differences between expected and transcribed text.

        Args:
            expected: Expected text
            transcribed: Transcribed text

        Returns:
            List of specific difference descriptions
        """
        issues = []

        expected_words = expected.split()
        transcribed_words = transcribed.split()

        # Check word count difference
        if len(expected_words) != len(transcribed_words):
            issues.append(
                f"Word count mismatch: expected {len(expected_words)} words, "
                f"heard {len(transcribed_words)} words"
            )

        # Compare individual words
        matcher = SequenceMatcher(None, expected_words, transcribed_words)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                expected_part = ' '.join(expected_words[i1:i2])
                transcribed_part = ' '.join(transcribed_words[j1:j2])
                issues.append(f"Said '{transcribed_part}' instead of '{expected_part}'")
            elif tag == 'delete':
                missing = ' '.join(expected_words[i1:i2])
                issues.append(f"Missing word(s): '{missing}'")
            elif tag == 'insert':
                extra = ' '.join(transcribed_words[j1:j2])
                issues.append(f"Extra word(s) detected: '{extra}'")

        return issues[:5]  # Limit to top 5 issues for clarity


    async def assess_word_pronunciation(
        self,
        audio_data: bytes,
        word: str,
        language: str = "en",
        filename: str = "word.ogg"
    ) -> Dict[str, Any]:
        """
        Simplified assessment for single word pronunciation.

        Args:
            audio_data: User's pronunciation audio
            word: The word they should pronounce
            language: Language code
            filename: Audio filename

        Returns:
            Assessment result with word-specific feedback
        """
        result = await self.assess_pronunciation(
            audio_data=audio_data,
            expected_text=word,
            language=language,
            filename=filename
        )

        if result.get("success"):
            # Add word-specific enhancements
            result["word"] = word
            result["attempts_recommended"] = 3 if not result["is_correct"] else 0

        return result
