import json
import logging
import time

from src.ai_provider import get_ai_provider
from src.prompt_manager import prompt_manager

logger = logging.getLogger(__name__)


class SimpleWordNormalizer:
    """Fast rule-based word normalization for common cases."""

    @staticmethod
    def normalize(word: str) -> str:
        """Apply simple normalization rules to a word."""
        if not word:
            return ""

        original_word = word

        # Basic cleanup
        word = word.lower().strip()

        # Skip very short words
        if len(word) <= 2:
            return word

        # Simple plural removal (English)
        if word.endswith("s") and len(word) > 3:
            # Handle special cases
            if word.endswith("ies") and len(word) > 4:
                normalized = word[:-3] + "y"  # flies -> fly, tries -> try
                logger.debug(f"SIMPLE NORMALIZATION: '{original_word}' -> '{normalized}' (ies->y rule)")
                return normalized
            elif word.endswith("es") and len(word) > 3:
                # Check if it's likely a plural
                if word.endswith(("ches", "shes", "xes", "zes")):
                    normalized = word[:-2]  # boxes -> box, wishes -> wish
                    logger.debug(f"SIMPLE NORMALIZATION: '{original_word}' -> '{normalized}' (es-> rule)")
                    return normalized
                elif word.endswith("ses") and len(word) > 4:
                    normalized = word[:-2]  # glasses -> glass
                    logger.debug(f"SIMPLE NORMALIZATION: '{original_word}' -> '{normalized}' (ses->s rule)")
                    return normalized
            else:
                # Simple -s removal for most cases
                normalized = word[:-1]  # cats -> cat, dogs -> dog
                logger.debug(f"SIMPLE NORMALIZATION: '{original_word}' -> '{normalized}' (s-> rule)")
                return normalized

        # Simple -er removal (comparative adjectives)
        if word.endswith("er") and len(word) > 3:
            # Only for likely adjectives, not all -er words
            if word in [
                "bigger",
                "smaller",
                "faster",
                "slower",
                "higher",
                "lower",
                "stronger",
                "weaker",
            ]:
                normalized = word[:-2]
                logger.debug(f"SIMPLE NORMALIZATION: '{original_word}' -> '{normalized}' (er-> comparative)")
                return normalized

        # Simple -est removal (superlative adjectives)
        if word.endswith("est") and len(word) > 4:
            # Only for likely adjectives
            if word in [
                "biggest",
                "smallest",
                "fastest",
                "slowest",
                "highest",
                "lowest",
                "strongest",
                "weakest",
            ]:
                normalized = word[:-3]
                logger.debug(f"SIMPLE NORMALIZATION: '{original_word}' -> '{normalized}' (est-> superlative)")
                return normalized

        if original_word.lower() != word:
            logger.debug(f"SIMPLE NORMALIZATION: '{original_word}' -> '{word}' (case normalization only)")

        return word


class WordNormalizer:
    """Normalize words to their base forms using an AI provider."""

    def __init__(self):
        self.ai_provider = get_ai_provider()

    async def normalize_words(self, words: list[str], language: str) -> dict[str, str]:
        """Normalize multiple words to their base forms using LLM."""
        if not words:
            return {}

        logger.info(f"AI_PROVIDER API: NORMALIZATION - {len(words)} words in {language}: {words}")
        start_time = time.time()

        # Create words list for prompt
        words_list = '["' + '", "'.join(words) + '"]'

        # Get prompts from prompt manager
        system_prompt = prompt_manager.get_system_prompt("word_normalization")
        user_prompt = prompt_manager.get_user_prompt("word_normalization", language=language, words_list=words_list)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response_str = await self.ai_provider.get_response(
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            result = json.loads(response_str)
            duration = time.time() - start_time

            logger.info(f"PERFORMANCE: Word normalization completed in {duration:.3f}s - {len(result)} words processed")
            for original, normalized in result.items():
                if original != normalized:
                    logger.debug(f"LLM NORMALIZATION: '{original}' -> '{normalized}'")

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"AI_PROVIDER API: NORMALIZATION FAILED - {words} in {duration:.3f}s: {e}")

            # Fallback: return words as-is if normalization fails
            return {word: word.lower().strip() for word in words}

    async def normalize_word(self, word: str, language: str) -> str:
        """Normalize a single word."""
        result = await self.normalize_words([word], language)
        return result.get(word, word.lower().strip())
