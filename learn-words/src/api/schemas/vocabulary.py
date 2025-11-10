"""Vocabulary management API schemas."""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class WordResponse(BaseModel):
    """Word data response."""

    id: int
    word: str
    from_language: str
    to_language: str
    short_translation: str
    medium_data: Dict[str, Any]
    long_data: Dict[str, Any]
    synonyms_native: List[str]
    synonyms_learning: List[str]
    word_type: Optional[str]
    native_language: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class WordStatsResponse(BaseModel):
    """User's statistics for a specific word."""

    user_id: int
    word_id: int
    total_attempts: int
    correct_answers: int
    success_rate: float = Field(..., description="Calculated success rate (0.0 to 1.0)")
    last_seen: Optional[datetime]
    is_marked_known: bool
    is_hidden: bool
    added_at: Optional[datetime]
    repetition_level: int
    next_review_at: Optional[datetime]
    priority_score: float = Field(..., description="Calculated priority score for training")

    class Config:
        from_attributes = True


class WordWithStatsResponse(BaseModel):
    """Word with user statistics."""

    word: WordResponse
    stats: WordStatsResponse


class VocabularyListResponse(BaseModel):
    """Paginated vocabulary list."""

    words: List[WordWithStatsResponse]
    total: int
    limit: int
    offset: int


class AddWordRequest(BaseModel):
    """Request to add a word to user's vocabulary."""

    user_id: int
    word_id: int


class MarkWordKnownRequest(BaseModel):
    """Request to mark word as known."""

    user_id: int
    word_id: int


class HideWordRequest(BaseModel):
    """Request to hide/unhide a word."""

    user_id: int
    word_id: int
    hidden: bool = Field(..., description="True to hide, False to unhide")


class VocabularyStatsResponse(BaseModel):
    """Overall vocabulary statistics for a user."""

    total_words: int
    known_words: int
    learning_words: int
    average_success_rate: float
    total_attempts: int
    total_correct: int
    words_due_for_review: int
