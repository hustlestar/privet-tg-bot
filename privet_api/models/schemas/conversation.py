"""Conversation-related schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import Field

from .base import BaseSchema, TimestampedSchema


class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EmotionType(str, Enum):
    """Detected emotion types."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"


class ConversationMessage(TimestampedSchema):
    """Conversation message schema."""
    
    id: int = Field(..., description="Message ID")
    user_id: int = Field(..., description="User ID")
    role: MessageRole = Field(..., description="Message role")
    message_text: Optional[str] = Field(None, description="Text message content")
    transcribed_text: Optional[str] = Field(None, description="Transcribed text from voice")
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="Sentiment score")
    emotion: Optional[EmotionType] = Field(None, description="Detected emotion")
    is_voice: bool = Field(False, description="Whether this was a voice message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ConversationRequest(BaseSchema):
    """Request to process a conversation message."""
    
    user_id: int = Field(..., description="User ID")
    message: str = Field(..., description="Message text")
    is_voice: bool = Field(False, description="Whether this is from voice")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ConversationResponse(BaseSchema):
    """Response from conversation processing."""
    
    response_text: str = Field(..., description="AI response text")
    emotion: Optional[EmotionType] = Field(None, description="Suggested emotion for response")
    facts_extracted: int = Field(0, description="Number of facts extracted")
    context_used: bool = Field(False, description="Whether context was used")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class ConversationHistory(BaseSchema):
    """Conversation history schema."""
    
    user_id: int = Field(..., description="User ID")
    messages: List[ConversationMessage] = Field(..., description="List of messages")
    total_messages: int = Field(..., description="Total message count")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range of messages")


class EmotionAnalysis(BaseSchema):
    """Emotion analysis result."""
    
    text: str = Field(..., description="Analyzed text")
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment score")
    primary_emotion: EmotionType = Field(..., description="Primary emotion")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    emotions: Dict[str, float] = Field(..., description="All emotion scores")
    voice_tone_suggestion: Optional[str] = Field(None, description="Suggested voice tone")