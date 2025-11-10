"""Data models for the Learn Words bot."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class ResponseMode(Enum):
    """User response preference modes."""

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class ExplanationLanguage(Enum):
    """User explanation language preference."""

    NATIVE = "native"  # Explanations in user's native language
    LEARNING = "learning"  # Explanations in target language (immersive)
    MIXED = "mixed"  # Key terms in learning, explanations in native


class TrainingType(Enum):
    """Types of training exercises."""

    DIRECT_TRANSLATION = "A"  # Learning language -> Native language
    MULTIPLE_CHOICE = "B"  # Learning language -> Choose from 4 options
    REVERSE_TRANSLATION = "C"  # Native language -> Learning language
    SYNONYM_CHOICE = "D"


class UserPlan(Enum):
    """User subscription plans."""

    FREE = "free"
    PLUS = "plus"
    PRO = "pro"


class NotificationType(Enum):
    """Types of notifications."""

    WORD_REVIEW = "repetition_reminder"
    ADS = "advertisement"
    INACTIVE_BUDGE = "budge_inactive"


@dataclass
class User:
    """User model."""

    user_id: int
    learning_language: str
    timezone: Optional[str] = None
    interface_language: str = "english"  # Language for bot interface
    response_mode: ResponseMode = ResponseMode.MEDIUM
    explanation_language: ExplanationLanguage = ExplanationLanguage.NATIVE
    plan: UserPlan = UserPlan.FREE
    created_at: Optional[datetime] = None
    notification_times: List[str] = None
    notification_times_count: int = 0
    is_blocked: bool = False
    telegram_handle: Optional[str] = None


@dataclass
class Word:
    """Word model with translations."""

    id: Optional[int]
    word: str
    from_language: str
    to_language: str
    short_translation: str
    medium_data: Dict[str, Any]  # {"word": str, "meaning": str, "example": str}
    long_data: Dict[str, Any]  # {"translations": List[str], "meanings": List[str], "examples": List[str], "context": str}
    synonyms_native: List[str] = None
    synonyms_learning: List[str] = None
    word_type: Optional[str] = None
    created_at: Optional[datetime] = None
    native_language: Optional[str] = None


@dataclass
class UserWordStats:
    """Statistics for a user's word learning progress."""

    user_id: int
    word_id: int
    total_attempts: int = 0
    correct_answers: int = 0
    last_seen: Optional[datetime] = None
    is_marked_known: bool = False
    is_hidden: bool = False
    added_at: Optional[datetime] = None
    repetition_level: int = 0
    next_review_at: Optional[datetime] = None

    @property
    def priority_score(self) -> float:
        """Calculate priority score for word selection."""
        # Lower success rate = higher priority
        success_rate = self.correct_answers / self.total_attempts if self.total_attempts > 0 else 0
        success_penalty = (1 - success_rate) * 100

        # Fewer attempts = higher priority (new words need practice)
        trial_penalty = max(0, (10 - self.total_attempts)) * 10

        # Time since last review
        if self.last_seen:
            days_since_review = (datetime.now() - self.last_seen).days
            time_bonus = min(days_since_review * 5, 50)
        else:
            time_bonus = 100  # Never seen before

        # Marked as known = lower priority but still included
        known_penalty = -30 if self.is_marked_known else 0

        return success_penalty + trial_penalty + time_bonus + known_penalty


@dataclass
class TrainingAttempt:
    """Record of a training attempt."""

    id: Optional[int]
    user_id: int
    word_id: int
    training_type: TrainingType
    is_correct: bool
    attempted_at: Optional[datetime] = None


@dataclass
class TranslationData:
    """Complete translation data from OpenAI."""

    word: str
    from_language: str
    to_language: str
    short: str
    synonyms_native: List[str]
    synonyms_learning: List[str]
    medium: Dict[str, str]
    long: Dict[str, Any]
    native_language: Optional[str] = None


@dataclass
class TrainingExercise:
    """A training exercise for the user."""

    word: Word
    training_type: TrainingType
    question: str
    correct_answer: str
    options: Optional[List[str]] = None  # For multiple choice
