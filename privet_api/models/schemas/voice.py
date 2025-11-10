"""Voice processing schemas."""

from typing import Optional, Dict, Any, List
from pydantic import Field

from .base import BaseSchema


class TranscriptionRequest(BaseSchema):
    """Request for voice transcription."""
    
    user_id: Optional[int] = Field(None, description="User ID")
    language: Optional[str] = Field(None, description="Language code for transcription")


class TranscriptionResponse(BaseSchema):
    """Response from voice transcription."""
    
    text: str = Field(..., description="Transcribed text")
    language: Optional[str] = Field(None, description="Detected language")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Transcription confidence")
    duration_seconds: Optional[float] = Field(None, description="Audio duration")


class SynthesisRequest(BaseSchema):
    """Request for text-to-speech synthesis."""
    
    text: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field(None, description="Voice ID or name")
    emotion: Optional[str] = Field(None, description="Emotion for synthesis")
    speed: float = Field(1.0, ge=0.25, le=4.0, description="Speech speed")
    language: Optional[str] = Field(None, description="Language code")


class SynthesisResponse(BaseSchema):
    """Response from text-to-speech synthesis."""
    
    audio_url: Optional[str] = Field(None, description="URL to download audio")
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio")
    duration_seconds: Optional[float] = Field(None, description="Audio duration")
    provider: str = Field(..., description="TTS provider used")
    voice: str = Field(..., description="Voice used")


class VoiceProcessingRequest(BaseSchema):
    """Complete voice processing request."""
    
    user_id: int = Field(..., description="User ID")
    language: Optional[str] = Field(None, description="Language code")


class VoiceProcessingResponse(BaseSchema):
    """Complete voice processing response."""
    
    transcribed_text: str = Field(..., description="Transcribed text")
    response_text: str = Field(..., description="AI response text")
    audio_url: Optional[str] = Field(None, description="Response audio URL")
    emotion_detected: Optional[str] = Field(None, description="Detected emotion")
    facts_extracted: int = Field(0, description="Number of facts extracted")
    processing_time_ms: int = Field(..., description="Total processing time")


class TTSProvider(BaseSchema):
    """TTS provider information."""
    
    name: str = Field(..., description="Provider name")
    voices: List[Dict[str, str]] = Field(..., description="Available voices")
    languages: List[str] = Field(..., description="Supported languages")
    features: Dict[str, Any] = Field(..., description="Provider features")