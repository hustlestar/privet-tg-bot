import json
import logging
import time
from typing import Dict

from src.ai_provider import get_ai_provider
from src.prompt_manager import prompt_manager

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect language of input text using LLM."""

    def __init__(self):
        self.ai_provider = get_ai_provider()

    async def detect_language(self, text: str, user_native: str, user_learning: str) -> Dict[str, str]:
        """Detect the language of input text and determine translation direction."""

        logger.info(f"AI_PROVIDER API: LANGUAGE_DETECTION - '{text}' (native: {user_native}, learning: {user_learning})")
        start_time = time.time()

        # Get prompts from prompt manager
        system_prompt = prompt_manager.get_system_prompt("language_detection")
        user_prompt = prompt_manager.get_user_prompt(
            "language_detection",
            text=text,
            user_native=user_native,
            user_learning=user_learning,
        )

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
            result = result[0] if isinstance(result, list) else result
            duration = time.time() - start_time

            # Validate required fields
            required_fields = [
                "detected_language",
                "confidence",
                "translation_direction",
                "from_language",
                "to_language",
            ]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            logger.info(f"PERFORMANCE: Language detection completed in {duration:.3f}s - detected: {result['detected_language']}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"AI_PROVIDER API: LANGUAGE_DETECTION FAILED - '{text}' in {duration:.3f}s: {e}")

            # Fallback: assume it's in learning language, translate to native
            return {
                "detected_language": user_learning,
                "confidence": "low",
                "translation_direction": "to_native",
                "from_language": user_learning,
                "to_language": user_native,
                "explanation": f"Language detection failed, defaulting to {user_learning} -> {user_native}",
            }
