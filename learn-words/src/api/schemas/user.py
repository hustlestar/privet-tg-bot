"""User management API schemas."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """Request to create a new user."""

    user_id: int
    learning_language: str
    interface_language: str = "english"
    response_mode: str = Field("medium", description="short, medium, or long")
    explanation_language: str = Field("native", description="native, learning, or mixed")
    plan: str = Field("free", description="free, plus, or pro")
    timezone: Optional[str] = "UTC"
    notification_times: Optional[List[str]] = None
    telegram_handle: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """Request to update user settings."""

    learning_language: Optional[str] = None
    interface_language: Optional[str] = None
    response_mode: Optional[str] = None
    explanation_language: Optional[str] = None
    plan: Optional[str] = None
    timezone: Optional[str] = None
    notification_times: Optional[List[str]] = None


class UserResponse(BaseModel):
    """User data response."""

    user_id: int
    learning_language: str
    interface_language: str
    response_mode: str
    explanation_language: str
    plan: str
    timezone: Optional[str]
    notification_times: List[str]
    notification_times_count: int
    created_at: Optional[datetime]
    is_blocked: bool
    telegram_handle: Optional[str]

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """User learning statistics."""

    user_id: int
    total_words: int
    known_words: int
    learning_words: int
    total_attempts: int
    total_correct: int
    success_rate: float
    recent_attempts: int = Field(..., description="Attempts in last 7 days")
    recent_correct: int = Field(..., description="Correct in last 7 days")
    recent_success_rate: float
    current_streak: int = Field(..., description="Current daily streak")
    last_activity: Optional[datetime]
