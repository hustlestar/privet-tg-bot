"""Vocabulary management API endpoints."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from src.dao.word_dao import WordDao
from src.dao.user_dao import UserDao
from src.api.deps import get_pool
from src.api.schemas.vocabulary import (
    WordResponse,
    WordStatsResponse,
    WordWithStatsResponse,
    VocabularyListResponse,
    AddWordRequest,
    MarkWordKnownRequest,
    HideWordRequest,
    VocabularyStatsResponse,
)

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("/{user_id}", response_model=VocabularyListResponse)
async def get_user_vocabulary(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_recent: bool = Query(True, description="Sort by most recent first"),
    include_hidden: bool = Query(False, description="Include hidden words"),
    pool=Depends(get_pool),
):
    """Get user's vocabulary list with statistics."""
    try:
        word_dao = WordDao(pool)
        user_dao = UserDao(pool)

        # Get words with stats
        words_data = await word_dao.get_user_vocabulary(
            user_id=user_id,
            limit=limit,
            offset=offset,
            sort_recent=sort_recent,
            include_hidden=include_hidden,
        )

        # Get total count
        total = await word_dao.get_user_vocabulary_count(user_id)

        # Convert to response format
        words_with_stats = []
        for word, stats in words_data:
            success_rate = (
                stats.correct_answers / stats.total_attempts
                if stats.total_attempts > 0
                else 0.0
            )

            word_response = WordResponse(
                id=word.id,
                word=word.word,
                from_language=word.from_language,
                to_language=word.to_language,
                short_translation=word.short_translation,
                medium_data=word.medium_data,
                long_data=word.long_data,
                synonyms_native=word.synonyms_native or [],
                synonyms_learning=word.synonyms_learning or [],
                word_type=word.word_type,
                native_language=word.native_language,
                created_at=word.created_at,
            )

            stats_response = WordStatsResponse(
                user_id=stats.user_id,
                word_id=stats.word_id,
                total_attempts=stats.total_attempts,
                correct_answers=stats.correct_answers,
                success_rate=success_rate,
                last_seen=stats.last_seen,
                is_marked_known=stats.is_marked_known,
                is_hidden=stats.is_hidden,
                added_at=stats.added_at,
                repetition_level=stats.repetition_level,
                next_review_at=stats.next_review_at,
                priority_score=stats.priority_score,
            )

            words_with_stats.append(
                WordWithStatsResponse(word=word_response, stats=stats_response)
            )

        return VocabularyListResponse(
            words=words_with_stats, total=total, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vocabulary: {str(e)}",
        )


@router.post("/{user_id}/words", status_code=status.HTTP_201_CREATED)
async def add_word_to_vocabulary(
    user_id: int,
    word_id: int = Query(..., description="Word ID to add"),
    pool=Depends(get_pool),
):
    """Add a word to user's vocabulary."""
    try:
        word_dao = WordDao(pool)
        await word_dao.add_word_to_user_vocabulary(user_id, word_id)
        return {"message": "Word added to vocabulary", "user_id": user_id, "word_id": word_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add word: {str(e)}",
        )


@router.delete("/{user_id}/words/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_word_from_vocabulary(
    user_id: int, word_id: int, pool=Depends(get_pool)
):
    """Remove a word from user's vocabulary."""
    try:
        word_dao = WordDao(pool)
        deleted = await word_dao.delete_word_from_vocabulary(user_id, word_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word {word_id} not found in user's vocabulary",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove word: {str(e)}",
        )


@router.patch("/{user_id}/words/{word_id}/known")
async def mark_word_as_known(user_id: int, word_id: int, pool=Depends(get_pool)):
    """Mark a word as known."""
    try:
        word_dao = WordDao(pool)
        success = await word_dao.mark_word_as_known(user_id, word_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word {word_id} not found in user's vocabulary",
            )

        return {"message": "Word marked as known"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark word as known: {str(e)}",
        )


@router.patch("/{user_id}/words/{word_id}/hidden")
async def toggle_word_hidden(
    user_id: int,
    word_id: int,
    hidden: bool = Query(..., description="True to hide, False to unhide"),
    pool=Depends(get_pool),
):
    """Hide or unhide a word."""
    try:
        word_dao = WordDao(pool)

        if hidden:
            success = await word_dao.hide_word_for_user(user_id, word_id)
            message = "Word hidden"
        else:
            success = await word_dao.unhide_word_for_user(user_id, word_id)
            message = "Word unhidden"

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word {word_id} not found in user's vocabulary",
            )

        return {"message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update word visibility: {str(e)}",
        )


@router.get("/{user_id}/stats", response_model=VocabularyStatsResponse)
async def get_vocabulary_stats(user_id: int, pool=Depends(get_pool)):
    """Get comprehensive vocabulary statistics for a user."""
    try:
        user_dao = UserDao(pool)
        stats = await user_dao.get_user_stats(user_id)

        # Calculate derived statistics
        success_rate = (
            stats["total_correct"] / stats["total_attempts"]
            if stats["total_attempts"] > 0
            else 0.0
        )

        return VocabularyStatsResponse(
            total_words=stats["total_words"],
            known_words=stats["known_words"],
            learning_words=stats["total_words"] - stats["known_words"],
            average_success_rate=success_rate,
            total_attempts=stats["total_attempts"],
            total_correct=stats["total_correct"],
            recent_attempts=stats["recent_attempts"],
            recent_correct=stats["recent_correct"],
            recent_success_rate=(
                stats["recent_correct"] / stats["recent_attempts"]
                if stats["recent_attempts"] > 0
                else 0.0
            ),
            current_streak=0,  # TODO: implement streak calculation
            last_activity=None,  # TODO: implement last activity tracking
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vocabulary stats: {str(e)}",
        )
