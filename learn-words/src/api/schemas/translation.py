"""Translation API schemas."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request to translate a word."""

    word: str = Field(..., min_length=1, description="Word to translate")
    from_language: str = Field(..., description="Source language code (e.g., 'en', 'es')")
    to_language: str = Field(..., description="Target language code")
    native_language: Optional[str] = Field(None, description="User's native language for context")


class SmartTranslationRequest(BaseModel):
    """Request for smart translation with auto language detection."""

    word: str = Field(..., min_length=1, description="Word to translate")
    user_native: str = Field(..., description="User's native language")
    user_learning: str = Field(..., description="Language user is learning")


class ParseSentenceRequest(BaseModel):
    """Request to parse a sentence into words."""

    sentence: str = Field(..., min_length=1, max_length=200, description="Sentence to parse")
    language: str = Field(..., description="Language of the sentence")


class TranslationResponse(BaseModel):
    """Complete translation data response."""

    word: str
    from_language: str
    to_language: str
    short_translation: str = Field(..., alias="short")
    medium_data: Dict[str, str] = Field(..., alias="medium")
    long_data: Dict[str, Any] = Field(..., alias="long")
    synonyms_native: List[str]
    synonyms_learning: List[str]
    native_language: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "word": "hello",
                "from_language": "en",
                "to_language": "es",
                "short": "hola",
                "medium": {
                    "word": "hola",
                    "meaning_native": "A greeting",
                    "meaning_learning": "Un saludo",
                    "example": "¡Hola! ¿Cómo estás?"
                },
                "long": {
                    "translations": ["hola", "buenos días", "buenas tardes"],
                    "meanings_native": ["A greeting", "An expression of greeting"],
                    "meanings_learning": ["Un saludo", "Una expresión de saludo"],
                    "examples": ["¡Hola! ¿Cómo estás?", "¡Hola! ¿Qué tal?"]
                },
                "synonyms_native": ["hi", "hey", "greetings"],
                "synonyms_learning": ["hola", "buenos días"],
                "native_language": "en"
            }
        }


class LanguageDetectionResult(BaseModel):
    """Language detection result."""

    detected_language: str
    confidence: str  # "low", "medium", "high"
    translation_direction: str  # "to_native", "to_learning", "ask_user"
    from_language: str
    to_language: str
    explanation: str


class SmartTranslationResponse(BaseModel):
    """Smart translation response with detection info."""

    translation: Optional[TranslationResponse]
    detection: LanguageDetectionResult


class ParsedSentenceResponse(BaseModel):
    """Parsed sentence response."""

    words: List[str] = Field(..., description="Extracted words")
    word_count: int = Field(..., description="Number of words extracted")
