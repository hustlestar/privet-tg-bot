"""Memory and RAG-related schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field

from .base import BaseSchema, TimestampedSchema


class UserFact(TimestampedSchema):
    """User fact schema."""
    
    id: int = Field(..., description="Fact ID")
    user_id: int = Field(..., description="User ID")
    fact_text: str = Field(..., description="Fact text")
    fact_summary: Optional[str] = Field(None, description="Fact summary")
    source_message_id: Optional[int] = Field(None, description="Source message ID")
    confidence: float = Field(1.0, ge=0, le=1, description="Fact confidence")
    category: Optional[str] = Field(None, description="Fact category")


class FactCreate(BaseSchema):
    """Schema for creating a fact."""
    
    user_id: int = Field(..., description="User ID")
    fact_text: str = Field(..., description="Fact text")
    fact_summary: Optional[str] = Field(None, description="Fact summary")
    category: Optional[str] = Field(None, description="Fact category")
    source_message_id: Optional[int] = Field(None, description="Source message ID")


class FactSearch(BaseSchema):
    """Schema for searching facts."""
    
    user_id: int = Field(..., description="User ID")
    query: str = Field(..., description="Search query")
    limit: int = Field(5, ge=1, le=50, description="Maximum results")
    min_similarity: float = Field(0.7, ge=0, le=1, description="Minimum similarity score")


class FactSearchResult(BaseSchema):
    """Fact search result."""
    
    fact: UserFact = Field(..., description="The fact")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score")
    relevance_reason: Optional[str] = Field(None, description="Why this fact is relevant")


class ProfileSummary(TimestampedSchema):
    """User profile summary schema."""
    
    id: int = Field(..., description="Summary ID")
    user_id: int = Field(..., description="User ID")
    summary_text: str = Field(..., description="Summary text")
    summary_topic: str = Field(..., description="Summary topic")
    last_updated: datetime = Field(..., description="Last update timestamp")


class ProfileSummaryCreate(BaseSchema):
    """Schema for creating/updating profile summary."""
    
    user_id: int = Field(..., description="User ID")
    summary_topic: str = Field("general", description="Summary topic")
    force_regenerate: bool = Field(False, description="Force regeneration")


class MemoryContext(BaseSchema):
    """Complete memory context for a user."""
    
    user_id: int = Field(..., description="User ID")
    relevant_facts: List[FactSearchResult] = Field(..., description="Relevant facts")
    profile_summaries: List[ProfileSummary] = Field(..., description="Profile summaries")
    recent_messages: List[Dict[str, Any]] = Field(..., description="Recent conversation messages")
    context_timestamp: datetime = Field(..., description="Context generation timestamp")


class MemoryStats(BaseSchema):
    """Memory statistics for a user."""
    
    user_id: int = Field(..., description="User ID")
    total_facts: int = Field(..., description="Total facts stored")
    fact_categories: Dict[str, int] = Field(..., description="Facts by category")
    profile_summaries_count: int = Field(..., description="Number of profile summaries")
    memory_density: float = Field(..., ge=0, description="Memory density score")
    last_fact_date: Optional[datetime] = Field(None, description="Date of last fact")
    storage_size_bytes: Optional[int] = Field(None, description="Storage size used")