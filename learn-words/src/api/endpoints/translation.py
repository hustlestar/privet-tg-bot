"""Translation API endpoints."""

from fastapi import APIRouter, HTTPException, status
from src.translation.translator import translator
from src.api.schemas.translation import (
    TranslationRequest,
    TranslationResponse,
    SmartTranslationRequest,
    SmartTranslationResponse,
    ParseSentenceRequest,
    ParsedSentenceResponse,
    LanguageDetectionResult,
)

router = APIRouter(prefix="/translation", tags=["translation"])


@router.post("/translate", response_model=TranslationResponse)
async def translate_word(request: TranslationRequest):
    """Translate a word with specified languages.

    Uses multi-tier caching:
    1. Simple normalization cache
    2. LLM normalization cache
    3. AI translation with caching

    Returns translation with 3 detail levels: short, medium, long.
    """
    try:
        translation_data = await translator.translate_word(
            word=request.word,
            from_language=request.from_language,
            to_language=request.to_language,
            native_language=request.native_language,
        )

        return TranslationResponse(
            word=translation_data.word,
            from_language=translation_data.from_language,
            to_language=translation_data.to_language,
            short=translation_data.short,
            medium=translation_data.medium,
            long=translation_data.long,
            synonyms_native=translation_data.synonyms_native or [],
            synonyms_learning=translation_data.synonyms_learning or [],
            native_language=translation_data.native_language,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}",
        )


@router.post("/translate/smart", response_model=SmartTranslationResponse)
async def smart_translate_word(request: SmartTranslationRequest):
    """Translate with automatic language detection.

    Automatically detects whether the word is in native or learning language
    and translates accordingly. Checks cache first before using AI.
    """
    try:
        translation_data, detection_result = await translator.smart_translate_word(
            word=request.word,
            user_native=request.user_native,
            user_learning=request.user_learning,
        )

        # Convert detection result to response model
        detection = LanguageDetectionResult(
            detected_language=detection_result["detected_language"],
            confidence=detection_result["confidence"],
            translation_direction=detection_result["translation_direction"],
            from_language=detection_result["from_language"],
            to_language=detection_result["to_language"],
            explanation=detection_result["explanation"],
        )

        # Convert translation data if available
        translation_response = None
        if translation_data:
            translation_response = TranslationResponse(
                word=translation_data.word,
                from_language=translation_data.from_language,
                to_language=translation_data.to_language,
                short=translation_data.short,
                medium=translation_data.medium,
                long=translation_data.long,
                synonyms_native=translation_data.synonyms_native or [],
                synonyms_learning=translation_data.synonyms_learning or [],
                native_language=translation_data.native_language,
            )

        return SmartTranslationResponse(
            translation=translation_response, detection=detection
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Smart translation failed: {str(e)}",
        )


@router.post("/parse-sentence", response_model=ParsedSentenceResponse)
async def parse_sentence(request: ParseSentenceRequest):
    """Parse a sentence into individual words for vocabulary selection.

    Extracts meaningful words, filtering out stop words and short words.
    Maximum 10 words per sentence.
    """
    try:
        words = await translator.parse_sentence_to_words(
            sentence=request.sentence, language=request.language
        )

        return ParsedSentenceResponse(words=words, word_count=len(words))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentence parsing failed: {str(e)}",
        )
