"""Pronunciation and TTS endpoints with caching."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
import base64

from privet_api.api.deps import get_pronunciation_service
from privet_api.services.pronunciation import PronunciationService
from privet_api.models.schemas.vocabulary import (
    PronunciationRequest,
    PronunciationResponse,
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
