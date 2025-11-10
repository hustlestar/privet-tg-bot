"""User-related schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field

from .base import BaseSchema, TimestampedSchema


class UserBase(BaseSchema):
    """Base user schema."""
    
    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    language: str = Field("en", description="User language code")


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    user_id: int = Field(..., description="Telegram user ID")


class UserUpdate(UserBase):
    """Schema for updating a user."""
    pass


class User(UserBase, TimestampedSchema):
    """Complete user schema."""
    
    user_id: int = Field(..., description="User ID")
    is_active: bool = Field(default=True, description="User active status")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class UserStats(BaseSchema):
    """User statistics schema."""
    
    user_id: int = Field(..., description="User ID")
    total_messages: int = Field(0, description="Total messages sent")
    total_voice_messages: int = Field(0, description="Total voice messages")
    total_facts: int = Field(0, description="Total facts stored")
    profile_summaries: int = Field(0, description="Number of profile summaries")
    memory_density: float = Field(0.0, description="Memory density score")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")