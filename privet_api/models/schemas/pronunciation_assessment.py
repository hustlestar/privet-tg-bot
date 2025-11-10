"""Schemas for pronunciation assessment API."""

from typing import Optional, List
from pydantic import BaseModel, Field


class PronunciationAssessmentResponse(BaseModel):
    """Response schema for pronunciation assessment."""
    success: bool
    accuracy_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Pronunciation accuracy score from 0-100"
    )
    transcribed_text: Optional[str] = Field(
        None,
        description="What the user actually said"
    )
    expected_text: Optional[str] = Field(
        None,
        description="What the user should have said"
    )
    is_correct: Optional[bool] = Field(
        None,
        description="Whether pronunciation is acceptable (>= 80%)"
    )
    feedback: Optional[str] = Field(
        None,
        description="Human-readable feedback message"
    )
    issues: Optional[List[str]] = Field(
        None,
        description="List of specific pronunciation issues"
    )
    language: Optional[str] = Field(
        None,
        description="Language code"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if success is False"
    )


class WordPronunciationAssessmentResponse(PronunciationAssessmentResponse):
    """Response schema for single word pronunciation assessment."""
    word: Optional[str] = Field(
        None,
        description="The word being assessed"
    )
    attempts_recommended: Optional[int] = Field(
        None,
        description="Number of additional practice attempts recommended"
    )


class PronunciationPracticeRequest(BaseModel):
    """Request schema for getting pronunciation practice material."""
    language: str = Field(
        ...,
        description="Target language code (en, es, ru)"
    )
    difficulty_level: Optional[str] = Field(
        "A1",
        description="CEFR difficulty level (A1-C2)"
    )
    category: Optional[str] = Field(
        None,
        description="Category of words to practice (e.g., 'greetings', 'numbers')"
    )
    count: int = Field(
        10,
        ge=1,
        le=50,
        description="Number of practice words to return"
    )


class PronunciationPracticeWord(BaseModel):
    """A word for pronunciation practice."""
    word: str
    translation: str
    phonetic: Optional[str] = None
    difficulty_level: str
    audio_url: Optional[str] = None
    example_sentence: Optional[str] = None


class PronunciationPracticeResponse(BaseModel):
    """Response schema for pronunciation practice material."""
    success: bool
    words: List[PronunciationPracticeWord] = Field(
        default_factory=list,
        description="List of words for practice"
    )
    language: str
    difficulty_level: str
    total_count: int
