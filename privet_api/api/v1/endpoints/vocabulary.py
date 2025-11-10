"""Vocabulary and word learning endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response

from privet_api.api.deps import (
    get_vocabulary_service,
    get_pronunciation_service,
)
from privet_api.services.vocabulary import VocabularyService
from privet_api.services.pronunciation import PronunciationService
from privet_api.models.schemas.vocabulary import (
    VocabularyWordCreate,
    VocabularyWordUpdate,
    VocabularyWordResponse,
    VocabularyWordListResponse,
    WordExtractionRequest,
    WordExtractionResponse,
    WordReviewRequest,
    WordReviewResponse,
    WordsForReviewRequest,
    WordsForReviewResponse,
    AdvancedTranslationRequest,
    AdvancedTranslationResponse,
)
from privet_api.models.schemas.base import ResponseSchema

router = APIRouter()


@router.post("/extract", response_model=WordExtractionResponse)
async def extract_words(
    request: WordExtractionRequest,
    vocab_service: VocabularyService = Depends(get_vocabulary_service),
) -> WordExtractionResponse:
    """Extract interesting words from text with translations.

    This endpoint analyzes text and extracts vocabulary words that might be
    useful for learning. It checks if the user already knows the words and
    provides translations.
    """
    try:
        extracted = await vocab_service.extract_words_from_text(
            text=request.text,
            target_language=request.target_language,
            native_language=request.native_language,
            user_id=request.user_id,
            max_words=request.max_words,
        )

        # Count unique words in text
        words_in_text = request.text.split()
        unique_words = len(set(words_in_text))

        return WordExtractionResponse(
            extracted_words=extracted,
            total_words=len(words_in_text),
            unique_words=unique_words,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting words: {str(e)}"
        )


@router.post("/words", response_model=VocabularyWordResponse, status_code=status.HTTP_201_CREATED)
async def add_word_to_vocabulary(
    word_data: VocabularyWordCreate,
    vocab_service: VocabularyService = Depends(get_vocabulary_service),
) -> VocabularyWordResponse:
    """Add a word to user's vocabulary.

    Creates a new vocabulary entry for the user. If auto_cache_pronunciation
    is enabled (default), the pronunciation will be automatically generated
    and cached.
    """
    try:
        word = await vocab_service.add_word_to_vocabulary(
            user_id=word_data.user_id,
            word_text=word_data.word_text,
            target_language=word_data.target_language,
            native_language=word_data.native_language,
            translation=word_data.translation,
            part_of_speech=word_data.part_of_speech,
            difficulty_level=word_data.difficulty_level,
            example_sentence=word_data.example_sentence,
            example_translation=word_data.example_translation,
            added_from_message_id=word_data.added_from_message_id,
            auto_cache_pronunciation=True,
        )

        if not word:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Word already exists in vocabulary"
            )

        return VocabularyWordResponse(**word)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding word: {str(e)}"
        )


@router.get("/words/{user_id}", response_model=VocabularyWordListResponse)
async def get_user_vocabulary(
    user_id: int,
    target_language: Optional[str] = Query(None, description="Filter by target language"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
    vocab_service: VocabularyService = Depends(get_vocabulary_service),
) -> VocabularyWordListResponse:
    """Get user's vocabulary with pagination.

    Returns a list of vocabulary words for the specified user, optionally
    filtered by target language.
    """
    try:
        result = await vocab_service.get_user_vocabulary(
            user_id=user_id,
            target_language=target_language,
            offset=offset,
            limit=limit,
        )

        return VocabularyWordListResponse(
            items=[VocabularyWordResponse(**w) for w in result["items"]],
            total=result["total"],
            offset=result["offset"],
            limit=result["limit"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching vocabulary: {str(e)}"
        )


@router.get("/words/{user_id}/stats")
async def get_vocabulary_stats(
    user_id: int,
    vocab_service: VocabularyService = Depends(get_vocabulary_service),
):
    """Get vocabulary learning statistics for a user.

    Returns statistics including total words, mastered words, words due for
    review, and average mastery level.
    """
    try:
        stats = await vocab_service.get_vocabulary_stats(user_id)
        return ResponseSchema(
            success=True,
            data=stats,
            message="Vocabulary statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )


@router.post("/review", response_model=WordReviewResponse)
async def review_word(
    review: WordReviewRequest,
    vocab_service: VocabularyService = Depends(get_vocabulary_service),
) -> WordReviewResponse:
    """Record a word review and update spaced repetition schedule.

    This endpoint is called when a user reviews a word (e.g., in flashcards).
    It updates the mastery level and calculates the next review date using
    spaced repetition algorithm.
    """
    try:
        result = await vocab_service.record_word_review(
            word_id=review.word_id,
            user_id=review.user_id,
            was_correct=review.was_correct,
            review_type=review.review_type,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Word not found or does not belong to user"
            )

        return WordReviewResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording review: {str(e)}"
        )


@router.post("/review/due", response_model=WordsForReviewResponse)
async def get_words_for_review(
    request: WordsForReviewRequest,
    vocab_service: VocabularyService = Depends(get_vocabulary_service),
) -> WordsForReviewResponse:
    """Get words that need review based on spaced repetition schedule.

    Returns words that are due for review, optionally filtered by review type:
    - "all": All active words
    - "due": Words due for review (default)
    - "mastered": Words with mastery level >= 4
    - "learning": Words with mastery level < 4
    """
    try:
        result = await vocab_service.get_words_for_review(
            user_id=request.user_id,
            limit=request.limit,
            review_type=request.review_type,
        )

        return WordsForReviewResponse(
            words=[VocabularyWordResponse(**w) for w in result["words"]],
            total_due=result["total_due"],
            total_learning=result["total_learning"],
            total_mastered=result["total_mastered"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching words for review: {str(e)}"
        )


@router.post("/translate/advanced", response_model=AdvancedTranslationResponse)
async def get_advanced_translation(
    request: AdvancedTranslationRequest,
    vocab_service: VocabularyService = Depends(get_vocabulary_service),
) -> AdvancedTranslationResponse:
    """Get advanced translation data from external API.

    **NOTE: This is currently a STUB endpoint**

    This endpoint will be integrated with your external translation API later.
    For now, it returns placeholder data to demonstrate the structure.

    The advanced translation includes:
    - Multiple translation options
    - Definitions in target language
    - Example sentences with translations
    - Synonyms and antonyms
    - Verb conjugations (if applicable)
    - Etymology and usage notes
    """
    try:
        result = await vocab_service.get_advanced_translation_stub(
            word=request.word,
            source_language=request.source_language,
            target_language=request.target_language,
            context=request.context,
        )

        return AdvancedTranslationResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching advanced translation: {str(e)}"
        )
