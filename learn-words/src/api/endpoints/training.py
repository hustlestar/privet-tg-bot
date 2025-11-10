"""Training and exercises API endpoints."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from src.dao.training_dao import TrainingDao
from src.dao.models import TrainingType, TrainingAttempt
from src.api.deps import get_pool
from src.api.schemas.training import (
    TrainingWordResponse,
    RecordAttemptRequest,
    RecordAttemptResponse,
    DistractorsResponse,
)

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/{user_id}/next", response_model=TrainingWordResponse)
async def get_next_training_word(user_id: int, pool=Depends(get_pool)):
    """Get the next word for training using priority algorithm.

    Priority calculation considers:
    - Success rate (lower = higher priority)
    - Attempt count (fewer = higher priority)
    - Time since last seen (longer = higher priority)
    - Known status (known words = lower priority)
    """
    try:
        training_dao = TrainingDao(pool)
        result = await training_dao.get_word_for_training(user_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No words available for training",
            )

        word, stats = result

        success_rate = (
            stats.correct_answers / stats.total_attempts
            if stats.total_attempts > 0
            else 0.0
        )

        return TrainingWordResponse(
            word_id=word.id,
            word=word.word,
            from_language=word.from_language,
            to_language=word.to_language,
            short_translation=word.short_translation,
            medium_data=word.medium_data,
            long_data=word.long_data,
            total_attempts=stats.total_attempts,
            correct_answers=stats.correct_answers,
            success_rate=success_rate,
            repetition_level=stats.repetition_level,
            last_seen=stats.last_seen,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training word: {str(e)}",
        )


@router.post("/attempts", response_model=RecordAttemptResponse)
async def record_training_attempt(
    attempt: RecordAttemptRequest, pool=Depends(get_pool)
):
    """Record a training attempt and update statistics.

    Updates:
    - Increments total_attempts
    - Increments correct_answers (if correct)
    - Updates last_seen timestamp
    - Calculates next review date using SM-2 spaced repetition
    - Updates repetition level
    """
    try:
        training_dao = TrainingDao(pool)

        # Convert training type string to enum
        training_type_map = {
            "A": TrainingType.DIRECT_TRANSLATION,
            "B": TrainingType.MULTIPLE_CHOICE,
            "C": TrainingType.REVERSE_TRANSLATION,
            "D": TrainingType.SYNONYM_CHOICE,
        }

        if attempt.training_type not in training_type_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid training_type. Must be one of: A, B, C, D",
            )

        training_type = training_type_map[attempt.training_type]

        # Create attempt object
        attempt_obj = TrainingAttempt(
            id=None,
            user_id=attempt.user_id,
            word_id=attempt.word_id,
            training_type=training_type,
            is_correct=attempt.is_correct,
        )

        # Record attempt
        attempt_id = await training_dao.record_training_attempt(
            attempt_obj, attempt.is_review_session
        )

        # Get updated stats to return new repetition level
        result = await training_dao.get_word_by_id_for_user(
            attempt.user_id, attempt.word_id
        )

        if result:
            _, stats = result
            return RecordAttemptResponse(
                attempt_id=attempt_id,
                new_repetition_level=stats.repetition_level,
                next_review_at=stats.next_review_at,
                message=(
                    "Correct! Great job!" if attempt.is_correct else "Try again next time!"
                ),
            )

        return RecordAttemptResponse(
            attempt_id=attempt_id,
            new_repetition_level=0,
            next_review_at=None,
            message="Attempt recorded",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record attempt: {str(e)}",
        )


@router.get("/{user_id}/distractors", response_model=DistractorsResponse)
async def get_translation_distractors(
    user_id: int,
    exclude_word_id: int = Query(..., description="Word ID to exclude (correct answer)"),
    to_language: str = Query(..., description="Target language"),
    count: int = Query(3, ge=1, le=10, description="Number of distractors"),
    pool=Depends(get_pool),
):
    """Get random translations for multiple choice distractors.

    Selects translations from user's vocabulary to create realistic options.
    """
    try:
        training_dao = TrainingDao(pool)
        distractors = await training_dao.get_random_translations_for_distractors(
            user_id=user_id,
            exclude_word_id=exclude_word_id,
            to_language=to_language,
            count=count,
        )

        return DistractorsResponse(distractors=distractors)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get distractors: {str(e)}",
        )
