"""Translation service using OpenAI API with smart language detection and enhanced native data."""

import json
import re
import time
import logging
from typing import Optional, List, Dict, Tuple

from src.ai_provider import get_ai_provider
from src.dao.models import TranslationData
from src.database import db
from src.prompt_manager import prompt_manager

# Configure logger for translation service
from src.translation.language_detector import LanguageDetector
from src.translation.word_normalizer import SimpleWordNormalizer, WordNormalizer
from src.utils import async_timer

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating words using OpenAI with smart language detection and enhanced native data."""

    def __init__(self):
        self.ai_provider = get_ai_provider()
        self.normalizer = WordNormalizer()
        self.simple_normalizer = SimpleWordNormalizer()
        self.language_detector = LanguageDetector()

    @async_timer
    async def smart_translate_word(
        self,
        word: str,
        user_native: str,
        user_learning: str,
        is_user_direction: bool = False,
    ) -> Tuple[TranslationData, Dict[str, str]]:
        """Translate a word with smart language detection and bidirectional logic."""

        logger.info(f"SMART TRANSLATION: Starting for '{word}' (native: {user_native}, learning: {user_learning})")

        # Step 0: Check if the word contains any letters.
        if not any(char.isalpha() for char in word):
            logger.info(f"SMART TRANSLATION: SKIPPING - '{word}' contains no letters.")
            return None, {
                "detected_language": "N/A",
                "confidence": "high",
                "translation_direction": "not_a_word",
                "from_language": "N/A",
                "to_language": "N/A",
                "explanation": "The input consists of symbols, numbers, or emojis, not a translatable word.",
            }

        # Step 1: Try learning -> native (most common for language learners)
        cached_result = await self._try_basic_cache_lookup(word, user_learning, user_native, user_native)
        if cached_result:
            logger.info(f"SMART TRANSLATION: SUCCESS - Found in cache ({user_learning} -> {user_native})")
            return cached_result, {
                "detected_language": user_learning.title(),
                "confidence": "high",
                "translation_direction": "to_native",
                "from_language": user_learning,
                "to_language": user_native,
                "explanation": f"Found in cache: {user_learning} -> {user_native}",
            }

        # Step 2: Try native -> learning
        cached_result = await self._try_basic_cache_lookup(word, user_native, user_learning, user_native)
        if cached_result:
            logger.info(f"SMART TRANSLATION: SUCCESS - Found in cache ({user_native} -> {user_learning})")
            return cached_result, {
                "detected_language": user_native.title(),
                "confidence": "high",
                "translation_direction": "to_learning",
                "from_language": user_native,
                "to_language": user_learning,
                "explanation": f"Found in cache: {user_native} -> {user_learning}",
            }

        # Step 3: No cache hit - proceed with language detection (LLM call)
        logger.info(f"SMART TRANSLATION: Cache miss - proceeding with language detection")
        detection_result = await self.language_detector.detect_language(word, user_native, user_learning)

        if detection_result["translation_direction"] == "ask_user":
            logger.info(f"SMART TRANSLATION: Language detection requires user input for '{word}'")
            # Return detection info for user to choose direction
            return None, detection_result

        # Proceed with translation
        from_lang = detection_result["from_language"]
        to_lang = detection_result["to_language"]

        logger.info(f"SMART TRANSLATION: Proceeding with '{word}' ({from_lang} -> {to_lang})")
        translation_data = await self.translate_word_enhanced(word, from_lang, to_lang, user_native, user_learning)

        return translation_data, detection_result

    @async_timer
    async def translate_word_enhanced(
        self,
        word: str,
        from_language: str,
        to_language: str,
        user_native: str,
        user_learning: str,
    ) -> TranslationData:
        """Translate a word with enhanced dual-language explanations and rich native data."""

        logger.info(f"TRANSLATION: Starting '{word}' ({from_language} -> {to_language})")
        overall_start_time = time.time()

        # Normalize languages
        from_language, to_language = self._normalize_languages(from_language, to_language)

        # If native_language is not provided, use the learning language
        native_language = user_native

        # Tier 1: Check cache with simple normalization
        simple_normalized = self.simple_normalizer.normalize(word)
        cached_result = await self._check_simple_normalization_cache(word, from_language, to_language, overall_start_time, native_language)
        if cached_result:
            return cached_result

        # Tier 3: Check cache with LLM normalization
        cached_result, normalized_word = await self._check_llm_normalization_cache(
            word,
            simple_normalized,
            from_language,
            to_language,
            overall_start_time,
            native_language,
        )
        if cached_result:
            return cached_result

        # Process the translation through API and caching
        return await self.translate_via_llm(
            word,
            normalized_word,
            from_language,
            to_language,
            user_native,
            user_learning,
            overall_start_time,
            native_language,
        )

    async def translate_word(
        self,
        word: str,
        from_language: str,
        to_language: str,
        native_language: Optional[str] = None,
    ) -> TranslationData:
        """Translate a word and return all three response modes (legacy method)."""
        # If native_language is not provided, use the learning language
        if native_language is None:
            native_language = to_language

        return await self.translate_word_enhanced(word, from_language, to_language, native_language, from_language)

    async def _try_basic_cache_lookup(
        self,
        word: str,
        from_lang: str,
        to_lang: str,
        native_language: Optional[str] = None,
    ) -> Optional[TranslationData]:
        """Try cache lookup with only basic normalization - no LLM calls."""
        # Simple normalization only
        simple_normalized = self.simple_normalizer.normalize(word)

        # Check cache
        cached_word = await db.get_word(simple_normalized, from_lang.lower(), to_lang.lower(), native_language)
        if cached_word:
            return TranslationData(
                word=cached_word.word,
                from_language=cached_word.from_language,
                to_language=cached_word.to_language,
                short=cached_word.short_translation,
                synonyms_native=cached_word.medium_data.get("synonyms_native", []),
                synonyms_learning=cached_word.medium_data.get("synonyms_learning", []),
                medium=cached_word.medium_data,
                long=cached_word.long_data,
                native_language=cached_word.native_language,
            )
        return None

    def _normalize_languages(self, from_language: str, to_language: str) -> Tuple[str, str]:
        """Normalize languages to lowercase for consistent caching."""
        return from_language.lower().strip(), to_language.lower().strip()

    def _create_translation_data_from_cache(self, cached_word) -> TranslationData:
        """Create TranslationData object from cached word data."""
        return TranslationData(
            word=cached_word.word,
            from_language=cached_word.from_language,
            to_language=cached_word.to_language,
            short=cached_word.short_translation,
            synonyms_native=cached_word.medium_data.get("synonyms_native", []),
            synonyms_learning=cached_word.medium_data.get("synonyms_learning", []),
            medium=cached_word.medium_data,
            long=cached_word.long_data,
            native_language=cached_word.native_language,
        )

    async def _check_simple_normalization_cache(
        self,
        word: str,
        from_language: str,
        to_language: str,
        overall_start_time: float,
        native_language: Optional[str] = None,
    ) -> Optional[TranslationData]:
        """Check cache with simple normalization (Tier 1)."""
        simple_normalized = self.simple_normalizer.normalize(word)
        logger.info(f"TIER 1: Simple normalization '{word}' -> '{simple_normalized}'")

        cached_word = await db.get_word(simple_normalized, from_language, to_language, native_language)
        if cached_word:
            duration = time.time() - overall_start_time
            logger.info(f"CACHE HIT: '{word}' ({from_language}->{to_language}) - Tier 1 Simple Normalization in {duration:.3f}s")
            logger.info(f"PERFORMANCE: Translation completed in {duration:.3f}s - CACHE")
            return self._create_translation_data_from_cache(cached_word)

        logger.info(f"CACHE MISS: '{simple_normalized}' ({from_language}->{to_language}) - Tier 1, proceeding to Tier 3")
        return None

    async def _check_llm_normalization_cache(
        self,
        word: str,
        simple_normalized: str,
        from_language: str,
        to_language: str,
        overall_start_time: float,
        native_language: Optional[str] = None,
    ) -> Tuple[Optional[TranslationData], str]:
        """Check cache with LLM normalization (Tier 3)."""
        llm_normalized = await self.normalizer.normalize_word(word, from_language)
        logger.info(f"TIER 3: LLM normalization '{word}' -> '{llm_normalized}'")

        if llm_normalized != simple_normalized:
            cached_word = await db.get_word(llm_normalized, from_language, to_language, native_language)
            if cached_word:
                duration = time.time() - overall_start_time
                logger.info(f"CACHE HIT: '{word}' ({from_language}->{to_language}) - Tier 3 LLM Normalization in {duration:.3f}s")
                logger.info(f"PERFORMANCE: Translation completed in {duration:.3f}s - CACHE")
                return (
                    self._create_translation_data_from_cache(cached_word),
                    llm_normalized,
                )

        logger.info(f"CACHE MISS: '{llm_normalized}' ({from_language}->{to_language}) - Tier 3, proceeding to AI_PROVIDER API")
        return None, llm_normalized

    async def _call_ai_provider_api(
        self,
        word: str,
        normalized_word: str,
        from_language: str,
        to_language: str,
        user_native: str,
        user_learning: str,
        native_language: Optional[str] = None,
    ) -> Tuple[dict, float, float]:
        """Make OpenAI API call for translation."""
        logger.info(f"AI_PROVIDER API: TRANSLATION - '{word}' -> '{normalized_word}' ({from_language} -> {to_language})")
        api_start_time = time.time()

        # Get prompts from prompt manager
        system_prompt = prompt_manager.get_system_prompt("translation")

        user_prompt = prompt_manager.get_user_prompt(
            "translation" if from_language == user_learning else "translation_indirect",
            word=word,
            from_language=from_language,
            to_language=to_language,
            user_native=user_native,
            user_learning=user_learning,
            normalized_word=normalized_word,
            native_language=native_language,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response_str = await self.ai_provider.get_response(
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            api_duration = time.time() - api_start_time
            logger.info(f"AI_PROVIDER API: TRANSLATION completed in {api_duration:.3f}s")

            # Parse the JSON response
            translation_json = json.loads(response_str)
            return translation_json, api_start_time, api_duration

        except json.JSONDecodeError as e:
            api_duration = time.time() - api_start_time
            logger.error(f"AI_PROVIDER API: TRANSLATION FAILED - JSON decode error in {api_duration:.3f}s: {e}")
            raise ValueError(f"Invalid JSON response from AI_PROVIDER: {e}")
        except Exception as e:
            api_duration = time.time() - api_start_time
            logger.error(f"AI_PROVIDER API: TRANSLATION FAILED - '{word}' ({from_language}->{to_language}) in {api_duration:.3f}s: {e}")
            raise ValueError(f"Translation failed: {e}")

    def _validate_and_process_response(self, translation_json: dict) -> dict:
        """Validate and process the API response."""
        # Validate required fields
        required_fields = [
            "word",
            "from_language",
            "to_language",
            "short",
            "synonyms_learning",
            "synonyms_native",
            "medium",
            "long",
        ]
        for field in required_fields:
            if field not in translation_json:
                raise ValueError(f"Missing required field: {field}")

        # Validate enhanced medium structure
        medium_required = ["word", "meaning_native", "meaning_learning", "example"]
        for field in medium_required:
            if field not in translation_json["medium"]:
                # Fallback for backward compatibility
                if field == "meaning_native" and "meaning" in translation_json["medium"]:
                    translation_json["medium"]["meaning_native"] = translation_json["medium"]["meaning"]
                    translation_json["medium"]["meaning_learning"] = translation_json["medium"]["meaning"]
                else:
                    translation_json["medium"][field] = ""

        # Validate enhanced long structure
        long_required = [
            "translations",
            "meanings_native",
            "meanings_learning",
            "examples",
        ]
        for field in long_required:
            if field not in translation_json["long"]:
                # Fallback for backward compatibility
                if field == "meanings_native" and "meanings" in translation_json["long"]:
                    translation_json["long"]["meanings_native"] = translation_json["long"]["meanings"]
                    translation_json["long"]["meanings_learning"] = translation_json["long"]["meanings"]
                else:
                    translation_json["long"][field] = []

        # Ensure optional fields exist with defaults
        optional_medium_fields = {"pronunciation": "", "grammar_info": ""}
        for field, default in optional_medium_fields.items():
            if field not in translation_json["medium"]:
                translation_json["medium"][field] = default

        optional_long_fields = {
            "cultural_context": "",
            "grammar_details": "",
            "pronunciation_guide": "",
            "usage_notes": "",
        }
        for field, default in optional_long_fields.items():
            if field not in translation_json["long"]:
                translation_json["long"][field] = default

        return translation_json

    def _create_translation_data(self, translation_json: dict) -> TranslationData:
        """Create TranslationData object from validated translation JSON."""
        return TranslationData(
            word=translation_json["word"],
            from_language=translation_json["from_language"],
            to_language=translation_json["to_language"],
            short=translation_json["short"],
            synonyms_native=translation_json["synonyms_native"],
            synonyms_learning=translation_json["synonyms_learning"],
            medium=translation_json["medium"],
            long=translation_json["long"],
            native_language=translation_json.get("native_language"),
        )

    async def _save_to_cache(
        self,
        translation_data: TranslationData,
        normalized_word: str,
        from_language: str,
        to_language: str,
        native_language: Optional[str] = None,
    ) -> None:
        """Save translation data to database cache."""
        try:
            await db.save_word(translation_data)
            context_info = f" with learning context: {native_language}" if native_language else ""
            logger.info(f"CACHE SAVE: Successfully cached '{normalized_word}' ({from_language}->{to_language}){context_info}")
        except Exception as e:
            # Log cache save error but don't fail the translation
            logger.warning(f"CACHE SAVE FAILED: '{normalized_word}' ({from_language}->{to_language}): {e}")

    async def translate_via_llm(
        self,
        word: str,
        normalized_word: str,
        from_language: str,
        to_language: str,
        user_native: str,
        user_learning: str,
        overall_start_time: float,
        native_language: Optional[str] = None,
    ) -> TranslationData:
        """Process translation API response, validate, and cache results.

        This method handles the OpenAI API call, response validation, data transformation,
        and database caching for translations.

        Args:
            word: Original word to translate
            normalized_word: Normalized form of the word
            from_language: Source language
            to_language: Target language
            user_native: User's native language
            user_learning: User's learning language
            overall_start_time: Start time of the overall translation process
            native_language:

        Returns:
            TranslationData object with complete translation information

        Raises:
            ValueError: If translation fails or response validation fails
        """
        try:
            # Call OpenAI API for translation
            translation_json, api_start_time, api_duration = await self._call_ai_provider_api(
                word,
                normalized_word,
                from_language,
                to_language,
                user_native,
                user_learning,
                native_language,
            )

            # Validate and process the response
            validated_json = self._validate_and_process_response(translation_json)

            # Add native_language if not present
            if "native_language" not in validated_json and native_language:
                validated_json["native_language"] = native_language

            # Create TranslationData object
            translation_data = self._create_translation_data(validated_json)

            # Save to database cache
            await self._save_to_cache(
                translation_data,
                normalized_word,
                from_language,
                to_language,
                native_language,
            )

            # Log performance metrics
            overall_duration = time.time() - overall_start_time
            logger.info(
                f"LLM TRANSLATION: Completed '{word}' -> '{translation_data.short}' ({from_language} -> {to_language}) in {overall_duration:.3f}s - API"
            )

            return translation_data

        except Exception as e:
            overall_duration = time.time() - overall_start_time
            logger.error(f"PERFORMANCE: Translation failed in {overall_duration:.3f}s - API ERROR")
            raise ValueError(f"Translation failed: {e}")

    async def smart_parse_sentence(self, sentence: str, user_native: str, user_learning: str) -> Tuple[List[str], Dict[str, str]]:
        """Parse sentence with smart language detection."""

        logger.info(f"SMART PARSING: Starting for '{sentence}' (native: {user_native}, learning: {user_learning})")

        # Step 1: Try to determine language from user settings first
        # Check if sentence might be in learning language by trying to parse it
        try:
            words_learning = await self.parse_sentence_to_words(sentence, user_learning)
            if words_learning:
                logger.info(f"SMART PARSING: SUCCESS - Parsed as {user_learning}")
                return words_learning, {
                    "detected_language": user_learning.title(),
                    "confidence": "high",
                    "translation_direction": "to_native",
                    "from_language": user_learning,
                    "to_language": user_native,
                    "explanation": f"Successfully parsed as {user_learning}",
                }
        except:
            pass

        # Step 2: Try native language
        try:
            words_native = await self.parse_sentence_to_words(sentence, user_native)
            if words_native:
                logger.info(f"SMART PARSING: SUCCESS - Parsed as {user_native}")
                return words_native, {
                    "detected_language": user_native.title(),
                    "confidence": "high",
                    "translation_direction": "to_learning",
                    "from_language": user_native,
                    "to_language": user_learning,
                    "explanation": f"Successfully parsed as {user_native}",
                }
        except:
            pass

        # Step 3: Fallback to language detection
        logger.info(f"SMART PARSING: Cache miss - proceeding with language detection")
        detection_result = await self.language_detector.detect_language(sentence, user_native, user_learning)

        if detection_result["translation_direction"] == "ask_user":
            logger.info(f"SMART PARSING: Language detection requires user input for '{sentence}'")
            return [], detection_result

        # Parse sentence in detected language
        detected_language = detection_result["detected_language"]
        logger.info(f"SMART PARSING: Proceeding with sentence parsing in {detected_language}")
        words = await self.parse_sentence_to_words(sentence, detected_language)

        return words, detection_result

    async def parse_sentence_to_words(self, sentence: str, language: str) -> list[str]:
        """Parse a sentence into individual words for vocabulary selection."""

        # Check sentence length limit
        words_in_sentence = sentence.split()
        if len(words_in_sentence) > 10:
            raise ValueError("Sentence is too long. Maximum 10 words allowed.")

        logger.info(f"AI_PROVIDER API: SENTENCE_PARSING - '{sentence}' ({language})")
        start_time = time.time()

        # Get prompts from prompt manager
        system_prompt = prompt_manager.get_system_prompt("sentence_parsing")
        user_prompt = prompt_manager.get_user_prompt("sentence_parsing", language=language, sentence=sentence)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response_str = await self.ai_provider.get_response(
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
            )

            result = json.loads(response_str)
            words = result.get("words", [])
            duration = time.time() - start_time

            logger.info(f"PERFORMANCE: Sentence parsing completed in {duration:.3f}s - extracted {len(words)} words")
            logger.debug(f"SENTENCE PARSING: '{sentence}' -> {words}")

            return words[:10]  # Limit to 10 words

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"AI_PROVIDER API: SENTENCE_PARSING FAILED - '{sentence}' in {duration:.3f}s: {e}")

            # Fallback: simple word splitting using stop words from prompt manager
            words = re.findall(r"\b\w+\b", sentence.lower())
            stop_words = set(prompt_manager.get_stop_words())
            filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
            logger.info(f"FALLBACK: Simple word splitting extracted {len(filtered_words)} words")
            return filtered_words[:10]


# Global translator instance
translator = TranslationService()
