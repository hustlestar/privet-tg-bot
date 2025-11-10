"""Pronunciation and TTS endpoints with caching."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import Response
import base64

from privet_api.api.deps import get_pronunciation_service, get_audio_service
from privet_api.services.pronunciation import PronunciationService
from privet_api.services.audio import AudioService
from privet_api.services.pronunciation.pronunciation_assessment import PronunciationAssessmentService
from privet_api.models.schemas.vocabulary import (
    PronunciationRequest,
    PronunciationResponse,
)
from privet_api.models.schemas.pronunciation_assessment import (
    PronunciationAssessmentResponse,
    WordPronunciationAssessmentResponse,
)
from privet_api.models.schemas.base import ResponseSchema

router = APIRouter()


@router.post("/synthesize", response_model=PronunciationResponse)
async def synthesize_pronunciation(
    request: PronunciationRequest,
    pronunciation_service: PronunciationService = Depends(get_pronunciation_service),
) -> PronunciationResponse:
    """Synthesize pronunciation for text with intelligent caching.

    This endpoint generates text-to-speech audio for the provided text.
    It automatically uses cached audio if available, significantly reducing
    API costs for frequently requested words.

    The caching is case-insensitive and normalizes whitespace, so "Hola",
    "hola", and " HOLA " will all use the same cached audio.

    Returns:
        - audio_data: Base64 encoded audio (MP3 format)
        - from_cache: Whether the audio was retrieved from cache
        - cache_id: ID of the cache entry (if cached)
    """
    try:
        audio_b64, from_cache, cache_id = await pronunciation_service.get_pronunciation_base64(
            text=request.text,
            language_code=request.language_code,
            voice_id=request.voice_id,
            use_cache=request.use_cache,
        )

        if not audio_b64:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate pronunciation audio"
            )

        # Get voice info
        voice_used = (
            request.voice_id
            or pronunciation_service._get_voice_for_language(request.language_code)
        )

        return PronunciationResponse(
            text=request.text,
            language_code=request.language_code,
            audio_data=audio_b64,
            audio_format="mp3",
            from_cache=from_cache,
            cache_id=cache_id,
            voice_id=voice_used,
            provider=pronunciation_service.audio_service.tts_provider_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error synthesizing pronunciation: {str(e)}"
        )


@router.post("/synthesize/audio", response_class=Response)
async def synthesize_pronunciation_audio(
    request: PronunciationRequest,
    pronunciation_service: PronunciationService = Depends(get_pronunciation_service),
) -> Response:
    """Synthesize pronunciation and return raw audio file.

    Same as /synthesize but returns the audio file directly instead of
    base64 encoded JSON. Useful for direct playback in audio players.

    Returns:
        Raw MP3 audio file
    """
    try:
        audio_bytes, from_cache, cache_id = await pronunciation_service.get_pronunciation(
            text=request.text,
            language_code=request.language_code,
            voice_id=request.voice_id,
            use_cache=request.use_cache,
        )

        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate pronunciation audio"
            )

        headers = {
            "X-From-Cache": str(from_cache).lower(),
            "X-Cache-ID": str(cache_id) if cache_id else "none",
        }

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers=headers,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error synthesizing pronunciation: {str(e)}"
        )


@router.post("/cache/bulk")
async def bulk_cache_words(
    words: list[str],
    language_code: str = Query(..., description="Language code (en, es, ru)"),
    voice_id: Optional[str] = Query(None, description="Voice ID override"),
    pronunciation_service: PronunciationService = Depends(get_pronunciation_service),
):
    """Pre-cache pronunciation for multiple words.

    This endpoint is useful for pre-populating the cache with common
    vocabulary to minimize API costs. It skips words that are already
    cached.

    Use this for:
    - Pre-caching common vocabulary lists (e.g., top 1000 Spanish words)
    - Preparing for lessons or quizzes
    - Bulk operations during off-peak hours
    """
    try:
        stats = await pronunciation_service.bulk_cache_words(
            words=words,
            language_code=language_code,
            voice_id=voice_id,
        )

        return ResponseSchema(
            success=True,
            data=stats,
            message=f"Bulk cache completed: {stats['cached']} cached, "
                   f"{stats['skipped']} skipped, {stats['failed']} failed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error bulk caching: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats(
    language_code: Optional[str] = Query(None, description="Filter by language code"),
    pronunciation_service: PronunciationService = Depends(get_pronunciation_service),
):
    """Get pronunciation cache statistics.

    Returns information about cache usage, including:
    - Total cached entries
    - Total storage size (bytes and MB)
    - Total cache hits (usage count)
    - Language-specific stats (if filtered)

    Use this to:
    - Monitor cache efficiency
    - Estimate storage requirements
    - Calculate cost savings
    """
    try:
        stats = await pronunciation_service.get_cache_stats(language_code)

        return ResponseSchema(
            success=True,
            data=stats,
            message="Cache statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cache stats: {str(e)}"
        )


@router.delete("/cache/cleanup")
async def cleanup_old_cache(
    days: int = Query(90, ge=1, le=365, description="Delete cache older than this many days"),
    pronunciation_service: PronunciationService = Depends(get_pronunciation_service),
):
    """Clean up old, rarely used cache entries.

    Deletes cache entries that:
    - Haven't been used in the specified number of days
    - Have only been used once (usage_count = 1)

    This helps manage storage by removing entries that are unlikely
    to be requested again.

    Default: 90 days
    """
    try:
        deleted_count = await pronunciation_service.cleanup_old_cache(days)

        return ResponseSchema(
            success=True,
            data={"deleted_count": deleted_count, "days_threshold": days},
            message=f"Cleaned up {deleted_count} old cache entries"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up cache: {str(e)}"
        )


# Pronunciation Assessment Endpoints

@router.post("/assess", response_model=PronunciationAssessmentResponse)
async def assess_pronunciation(
    audio_file: UploadFile = File(..., description="Audio file of user's pronunciation"),
    expected_text: str = Form(..., description="The text the user should pronounce"),
    language: str = Form("en", description="Language code (en, es, ru)"),
    audio_service: AudioService = Depends(get_audio_service),
) -> PronunciationAssessmentResponse:
    """Assess pronunciation quality by comparing user's audio to expected text.

    This endpoint:
    1. Transcribes the user's audio using Whisper STT
    2. Compares it to the expected text
    3. Calculates an accuracy score (0-100)
    4. Provides specific feedback and identifies issues

    Accuracy thresholds:
    - 90-100: Excellent
    - 80-89: Good (acceptable)
    - 60-79: Fair (needs practice)
    - 0-59: Poor (needs significant practice)

    Returns:
        - accuracy_score: 0-100 pronunciation accuracy
        - transcribed_text: What was actually said
        - is_correct: Boolean if score >= 80%
        - feedback: Human-readable feedback
        - issues: List of specific pronunciation problems
    """
    try:
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        audio_bytes = await audio_file.read()
        if len(audio_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file too large. Maximum size is 10MB"
            )

        # Validate file type
        allowed_types = ["audio/ogg", "audio/mpeg", "audio/wav", "audio/webm", "audio/mp4", "audio/x-m4a"]
        if audio_file.content_type and audio_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )

        # Create assessment service
        assessment_service = PronunciationAssessmentService(audio_service)

        # Assess pronunciation
        result = await assessment_service.assess_pronunciation(
            audio_data=audio_bytes,
            expected_text=expected_text,
            language=language,
            filename=audio_file.filename or "pronunciation.ogg"
        )

        return PronunciationAssessmentResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assessing pronunciation: {str(e)}"
        )


@router.post("/assess/word", response_model=WordPronunciationAssessmentResponse)
async def assess_word_pronunciation(
    audio_file: UploadFile = File(..., description="Audio file of user pronouncing a single word"),
    word: str = Form(..., description="The word the user should pronounce"),
    language: str = Form("en", description="Language code (en, es, ru)"),
    audio_service: AudioService = Depends(get_audio_service),
) -> WordPronunciationAssessmentResponse:
    """Simplified pronunciation assessment for a single word.

    This is optimized for single-word pronunciation practice, providing:
    - Word-specific feedback
    - Recommended number of retry attempts
    - Simpler assessment logic

    Use this for:
    - Vocabulary word practice
    - Pronunciation drills
    - Quick pronunciation checks

    Returns same fields as /assess plus:
        - word: The word being assessed
        - attempts_recommended: How many more times to practice (0 if good)
    """
    try:
        # Validate file size
        max_size = 5 * 1024 * 1024  # 5MB for single words
        audio_bytes = await audio_file.read()
        if len(audio_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file too large. Maximum size is 5MB for word assessment"
            )

        # Create assessment service
        assessment_service = PronunciationAssessmentService(audio_service)

        # Assess word pronunciation
        result = await assessment_service.assess_word_pronunciation(
            audio_data=audio_bytes,
            word=word,
            language=language,
            filename=audio_file.filename or "word.ogg"
        )

        return WordPronunciationAssessmentResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assessing word pronunciation: {str(e)}"
        )
