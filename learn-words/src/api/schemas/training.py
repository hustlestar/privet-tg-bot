"""Training and exercises API schemas."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TrainingWordResponse(BaseModel):
    """Word selected for training with its stats."""

    word_id: int
    word: str
    from_language: str
    to_language: str
    short_translation: str
    medium_data: dict
    long_data: dict
    total_attempts: int
    correct_answers: int
    success_rate: float
    repetition_level: int
    last_seen: Optional[datetime]


class RecordAttemptRequest(BaseModel):
    """Request to record a training attempt."""

    user_id: int
    word_id: int
    training_type: str = Field(..., description="Type: 'A' (direct), 'B' (multiple choice), 'C' (reverse), 'D' (synonym)")
    is_correct: bool
    is_review_session: bool = Field(False, description="Whether this is a scheduled review")


class RecordAttemptResponse(BaseModel):
    """Response after recording attempt."""

    attempt_id: int
    new_repetition_level: int
    next_review_at: Optional[datetime]
    message: str


class MultipleChoiceExercise(BaseModel):
    """Multiple choice exercise data."""

    word_id: int
    question_word: str
    from_language: str
    to_language: str
    correct_answer: str
    options: List[str] = Field(..., description="4 options including correct answer")


class SynonymOption(BaseModel):
    """Option for synonym matching exercise."""

    word_id: int
    word: str
    translation: str


class SynonymMatchExercise(BaseModel):
    """Synonym matching exercise data."""

    target_word_id: int
    target_word: str
    target_translation: str
    options: List[SynonymOption] = Field(..., description="Words to match")
    correct_option_id: int


class DistractorsResponse(BaseModel):
    """Random distractor options."""

    distractors: List[str] = Field(..., description="Random translations for multiple choice")
