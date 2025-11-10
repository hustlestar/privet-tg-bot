"""Schemas for progress tracking and gamification."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UserProgressResponse(BaseModel):
    """User progress data."""
    user_id: int
    total_xp: int
    current_level: int
    xp_to_next_level: int
    current_streak: int
    longest_streak: int
    total_study_time_seconds: int
    total_sessions: int
    last_activity_date: Optional[datetime]
    created_at: datetime


class UserStatisticsResponse(BaseModel):
    """Comprehensive user statistics."""
    user_id: int
    total_xp: int
    current_level: int
    xp_to_next_level: int
    current_streak: int
    longest_streak: int
    total_study_time_seconds: int
    total_sessions: int
    last_activity_date: Optional[datetime]
    avg_session_duration: int
    created_at: datetime


class AddXPRequest(BaseModel):
    """Request to add XP to user."""
    user_id: int
    xp_amount: int = Field(ge=0, le=10000)
    activity_type: Optional[str] = "general"


class RecordSessionRequest(BaseModel):
    """Request to record a learning session."""
    user_id: int
    session_type: str = Field(..., description="Type: conversation, grammar, pronunciation, review")
    duration_seconds: int = Field(ge=0, le=86400, description="Duration in seconds (max 24h)")
    xp_earned: int = Field(ge=0, le=1000, description="XP earned this session")


class AchievementResponse(BaseModel):
    """Achievement data."""
    id: int
    achievement_code: str
    title_en: str
    title_es: Optional[str]
    title_ru: Optional[str]
    description_en: str
    description_es: Optional[str]
    description_ru: Optional[str]
    icon: Optional[str]
    xp_reward: int
    category: str
    difficulty: str
    is_active: bool


class UserAchievementResponse(AchievementResponse):
    """Achievement with user-specific earned data."""
    earned_at: datetime
    earned_metadata: Optional[dict]


class AwardAchievementRequest(BaseModel):
    """Request to award achievement to user."""
    user_id: int
    achievement_code: str
    metadata: Optional[dict] = None


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    total_xp: int
    current_level: int
    longest_streak: int
    total_study_time_seconds: int
    current_streak: int


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""
    metric: str
    entries: List[LeaderboardEntry]
    total_count: int
