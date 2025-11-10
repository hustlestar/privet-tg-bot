"""Vocabulary and language learning schemas."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseSchema, TimestampedSchema


# ===== Vocabulary Word Schemas =====

class VocabularyWordBase(BaseSchema):
    """Base vocabulary word schema."""

    word_text: str = Field(..., description="The actual word or phrase", max_length=255)
    target_language: str = Field(..., description="Language of the word (es, en, ru)", max_length=10)
    native_language: str = Field(..., description="User's native language", max_length=10)
    translation: Optional[str] = Field(None, description="Simple translation")
    part_of_speech: Optional[str] = Field(None, description="noun, verb, adjective, etc.", max_length=50)
    difficulty_level: Optional[str] = Field(None, description="A1, A2, B1, B2, C1, C2", max_length=10)
    example_sentence: Optional[str] = Field(None, description="Example usage")
    example_translation: Optional[str] = Field(None, description="Translation of example")
    pronunciation_ipa: Optional[str] = Field(None, description="IPA phonetic notation", max_length=255)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional data (context, synonyms, etc.)")


class VocabularyWordCreate(VocabularyWordBase):
    """Schema for creating a vocabulary word."""

    user_id: int = Field(..., description="User ID")
    added_from_message_id: Optional[int] = Field(None, description="Message ID where word was found")


class VocabularyWordUpdate(BaseSchema):
    """Schema for updating a vocabulary word."""

    translation: Optional[str] = None
    part_of_speech: Optional[str] = None
    difficulty_level: Optional[str] = None
    example_sentence: Optional[str] = None
    example_translation: Optional[str] = None
    pronunciation_ipa: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class VocabularyWordResponse(VocabularyWordBase):
    """Schema for vocabulary word response."""

    id: int = Field(..., description="Word ID")
    user_id: int = Field(..., description="User ID")
    normalized_form: str = Field(..., description="Normalized form for matching")
    pronunciation_cache_id: Optional[int] = Field(None, description="Pronunciation cache ID")
    pronunciation_url: Optional[str] = Field(None, description="URL to pronunciation audio")
    added_from_message_id: Optional[int] = None
    times_reviewed: int = Field(0, description="Number of times reviewed")
    times_correct: int = Field(0, description="Number of correct reviews")
    mastery_level: int = Field(0, description="Mastery level (0-5 stars)")
    is_active: bool = Field(True, description="Whether word is active")
    last_reviewed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = Field(None, description="Next spaced repetition review")
    created_at: datetime
    updated_at: datetime


class VocabularyWordListResponse(BaseSchema):
    """Schema for list of vocabulary words."""

    items: List[VocabularyWordResponse] = Field(..., description="List of vocabulary words")
    total: int = Field(..., description="Total number of words")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")


# ===== Word Extraction Schemas =====

class WordExtractionRequest(BaseSchema):
    """Request schema for extracting words from text."""

    text: str = Field(..., description="Text to extract words from")
    target_language: str = Field(..., description="Language of the text", max_length=10)
    native_language: str = Field(..., description="User's native language for translation", max_length=10)
    user_id: Optional[int] = Field(None, description="User ID for filtering known words")
    max_words: int = Field(10, ge=1, le=50, description="Maximum number of words to extract")


class ExtractedWord(BaseSchema):
    """Schema for an extracted word."""

    word: str = Field(..., description="The extracted word")
    translation: str = Field(..., description="Translation")
    part_of_speech: Optional[str] = Field(None, description="Part of speech")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    context: Optional[str] = Field(None, description="Context where word appears")
    is_known: bool = Field(False, description="Whether user already knows this word")


class WordExtractionResponse(BaseSchema):
    """Response schema for word extraction."""

    extracted_words: List[ExtractedWord] = Field(..., description="List of extracted words")
    total_words: int = Field(..., description="Total words in text")
    unique_words: int = Field(..., description="Unique words found")


# ===== Pronunciation Cache Schemas =====

class PronunciationCacheBase(BaseSchema):
    """Base pronunciation cache schema."""

    word_text: str = Field(..., description="The word or phrase", max_length=255)
    language_code: str = Field(..., description="Language code", max_length=10)
    voice_id: str = Field(..., description="TTS voice identifier", max_length=100)
    provider: str = Field(..., description="TTS provider", max_length=50)


class PronunciationCacheCreate(PronunciationCacheBase):
    """Schema for creating pronunciation cache entry."""

    audio_format: str = Field("mp3", description="Audio file format", max_length=20)
    audio_data: str = Field(..., description="Base64 encoded audio data")
    file_size_bytes: int = Field(..., description="Size of decoded audio")
    duration_seconds: Optional[int] = Field(None, description="Audio duration")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate")
    ipa_pronunciation: Optional[str] = Field(None, description="IPA phonetic notation", max_length=255)


class PronunciationCacheResponse(PronunciationCacheBase):
    """Schema for pronunciation cache response."""

    id: int = Field(..., description="Cache ID")
    normalized_form: str = Field(..., description="Normalized form")
    audio_format: str
    audio_url: Optional[str] = Field(None, description="URL to audio file")
    file_size_bytes: int
    duration_seconds: Optional[int] = None
    sample_rate: Optional[int] = None
    ipa_pronunciation: Optional[str] = None
    usage_count: int = Field(1, description="Times this cache was used")
    created_at: datetime
    last_used_at: datetime


class PronunciationRequest(BaseSchema):
    """Request schema for pronunciation."""

    text: str = Field(..., description="Text to pronounce", max_length=500)
    language_code: str = Field(..., description="Language code", max_length=10)
    voice_id: Optional[str] = Field(None, description="Preferred voice ID")
    use_cache: bool = Field(True, description="Whether to use cached pronunciation")


class PronunciationResponse(BaseSchema):
    """Response schema for pronunciation."""

    text: str = Field(..., description="The text")
    language_code: str
    audio_data: str = Field(..., description="Base64 encoded audio")
    audio_format: str = Field("mp3", description="Audio format")
    from_cache: bool = Field(False, description="Whether pronunciation was from cache")
    cache_id: Optional[int] = Field(None, description="Cache ID if cached")
    voice_id: str = Field(..., description="Voice used")
    provider: str = Field(..., description="TTS provider used")


# ===== Learning Session Schemas =====

class LearningSessionBase(BaseSchema):
    """Base learning session schema."""

    session_type: str = Field(..., description="conversation, flashcard, quiz, review", max_length=50)
    words_studied: Optional[List[int]] = Field(None, description="List of vocabulary word IDs")
    correct_count: int = Field(0, ge=0, description="Number of correct answers")
    incorrect_count: int = Field(0, ge=0, description="Number of incorrect answers")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Session duration")
    xp_earned: int = Field(0, ge=0, description="Experience points earned")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session data")


class LearningSessionCreate(LearningSessionBase):
    """Schema for creating a learning session."""

    user_id: int = Field(..., description="User ID")


class LearningSessionUpdate(BaseSchema):
    """Schema for updating a learning session."""

    ended_at: Optional[datetime] = Field(None, description="Session end time")
    correct_count: Optional[int] = None
    incorrect_count: Optional[int] = None
    duration_seconds: Optional[int] = None
    xp_earned: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class LearningSessionResponse(LearningSessionBase):
    """Schema for learning session response."""

    id: int = Field(..., description="Session ID")
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None


# ===== User Language Settings Schemas =====

class UserLanguageSettingsBase(BaseSchema):
    """Base user language settings schema."""

    target_language: str = Field(..., description="Language being learned", max_length=10)
    native_language: str = Field(..., description="User's native language", max_length=10)
    proficiency_level: Optional[str] = Field(None, description="A1, A2, B1, B2, C1, C2", max_length=10)
    daily_word_goal: int = Field(10, ge=1, le=100, description="Daily word learning goal")
    preferred_tts_voice: Optional[str] = Field(None, description="Preferred TTS voice", max_length=100)
    learning_preferences: Optional[Dict[str, Any]] = Field(None, description="Additional preferences")


class UserLanguageSettingsCreate(UserLanguageSettingsBase):
    """Schema for creating user language settings."""

    user_id: int = Field(..., description="User ID")


class UserLanguageSettingsUpdate(BaseSchema):
    """Schema for updating user language settings."""

    target_language: Optional[str] = None
    native_language: Optional[str] = None
    proficiency_level: Optional[str] = None
    daily_word_goal: Optional[int] = None
    preferred_tts_voice: Optional[str] = None
    learning_preferences: Optional[Dict[str, Any]] = None


class UserLanguageSettingsResponse(UserLanguageSettingsBase):
    """Schema for user language settings response."""

    id: int = Field(..., description="Settings ID")
    user_id: int
    daily_streak: int = Field(0, description="Consecutive days of learning")
    total_xp: int = Field(0, description="Total experience points")
    current_level: int = Field(1, description="Gamification level")
    last_active_date: Optional[datetime] = Field(None, description="Last learning activity")
    created_at: datetime
    updated_at: datetime


# ===== Word Review Schemas =====

class WordReviewRequest(BaseSchema):
    """Request schema for reviewing a word."""

    word_id: int = Field(..., description="Vocabulary word ID")
    user_id: int = Field(..., description="User ID")
    was_correct: bool = Field(..., description="Whether the review was correct")
    review_type: str = Field("flashcard", description="Type of review", max_length=50)


class WordReviewResponse(BaseSchema):
    """Response schema for word review."""

    word_id: int
    new_mastery_level: int = Field(..., description="Updated mastery level")
    next_review_at: Optional[datetime] = Field(None, description="Next scheduled review")
    xp_earned: int = Field(0, description="XP earned from this review")


class WordsForReviewRequest(BaseSchema):
    """Request schema for getting words for review."""

    user_id: int = Field(..., description="User ID")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of words")
    review_type: str = Field("due", description="all, due, mastered, learning")


class WordsForReviewResponse(BaseSchema):
    """Response schema for words for review."""

    words: List[VocabularyWordResponse] = Field(..., description="Words to review")
    total_due: int = Field(..., description="Total words due for review")
    total_learning: int = Field(..., description="Total words being learned")
    total_mastered: int = Field(..., description="Total mastered words")


# ===== Advanced Translation Stub Schema =====

class AdvancedTranslationRequest(BaseSchema):
    """Request schema for advanced translation (stub for external API)."""

    word: str = Field(..., description="Word to translate", max_length=255)
    source_language: str = Field(..., description="Source language", max_length=10)
    target_language: str = Field(..., description="Target language", max_length=10)
    context: Optional[str] = Field(None, description="Context for better translation")


class AdvancedTranslationResponse(BaseSchema):
    """Response schema for advanced translation (stub)."""

    word: str
    translations: List[str] = Field(..., description="List of possible translations")
    definitions: List[str] = Field([], description="Definitions in target language")
    examples: List[Dict[str, str]] = Field([], description="Example sentences with translations")
    synonyms: List[str] = Field([], description="Synonyms")
    antonyms: List[str] = Field([], description="Antonyms")
    conjugations: Optional[Dict[str, Any]] = Field(None, description="Verb conjugations if applicable")
    etymology: Optional[str] = Field(None, description="Word origin")
    usage_notes: Optional[str] = Field(None, description="Usage notes")
    stub_message: str = Field(
        "Advanced translation feature will be integrated with external API",
        description="Placeholder message"
    )
