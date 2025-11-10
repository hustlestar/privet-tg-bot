"""Streaming chat schemas for SSE (Server-Sent Events)."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from .base import BaseSchema


class StreamingChatRequest(BaseSchema):
    """Request schema for streaming chat."""

    user_id: int = Field(..., description="User ID")
    message: str = Field(..., description="User message text")
    target_language: str = Field(..., description="Target language for learning", max_length=10)
    native_language: str = Field(..., description="User's native language", max_length=10)
    include_vocabulary_hints: bool = Field(True, description="Whether to include vocabulary extraction")
    include_grammar_hints: bool = Field(True, description="Whether to include grammar hints")
    conversation_context_limit: int = Field(5, ge=1, le=20, description="Number of previous messages to include")


class StreamingMessageChunk(BaseSchema):
    """Schema for a single chunk in the streaming response."""

    type: str = Field(..., description="Chunk type: text, word, grammar, done, error")
    content: str = Field("", description="Chunk content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WordMetadata(BaseSchema):
    """Metadata for a word in streaming response."""

    word: str = Field(..., description="The word")
    translation: Optional[str] = Field(None, description="Translation")
    part_of_speech: Optional[str] = Field(None, description="Part of speech")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    pronunciation_cache_id: Optional[int] = Field(None, description="Pronunciation cache ID")
    is_known: bool = Field(False, description="Whether user already knows this word")


class StreamingWordChunk(StreamingMessageChunk):
    """Schema for word chunk with interactive metadata."""

    type: str = Field("word", description="Always 'word'")
    content: str = Field(..., description="The word text")
    metadata: WordMetadata = Field(..., description="Word metadata for interactivity")


class GrammarHint(BaseSchema):
    """Schema for grammar hint in streaming response."""

    rule_id: Optional[int] = Field(None, description="Grammar rule ID")
    category: str = Field(..., description="Grammar category")
    hint: str = Field(..., description="Grammar hint text")
    example: Optional[str] = Field(None, description="Example")


class StreamingGrammarChunk(StreamingMessageChunk):
    """Schema for grammar hint chunk."""

    type: str = Field("grammar", description="Always 'grammar'")
    metadata: GrammarHint = Field(..., description="Grammar hint data")


class StreamingDoneChunk(StreamingMessageChunk):
    """Schema for completion chunk."""

    type: str = Field("done", description="Always 'done'")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Final metadata (message_id, session_id, etc.)")


class StreamingErrorChunk(StreamingMessageChunk):
    """Schema for error chunk."""

    type: str = Field("error", description="Always 'error'")
    content: str = Field(..., description="Error message")
    metadata: Optional[Dict[str, str]] = Field(None, description="Error details")
