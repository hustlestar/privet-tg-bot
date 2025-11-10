"""Progress tracking and gamification endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from asyncpg import Pool

from privet_api.api.deps import get_db_pool
from privet_api.repositories.progress_repository import ProgressRepository
from privet_api.models.schemas.progress import (
    UserProgressResponse,
    UserStatisticsResponse,
    AddXPRequest,
    RecordSessionRequest,
    AchievementResponse,
    UserAchievementResponse,
    AwardAchievementRequest,
    LeaderboardEntry,
    LeaderboardResponse,
)
from privet_api.models.schemas.base import ResponseSchema

router = APIRouter()


@router.get("/{user_id}", response_model=ResponseSchema)
async def get_user_progress(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool),
):
    """Get user's current progress including XP, level, and streak.

    Returns:
        - total_xp: Total experience points
        - current_level: Current level (1-100)
        - xp_to_next_level: XP needed for next level
        - current_streak: Current daily learning streak
        - longest_streak: Longest streak achieved
        - total_study_time_seconds: Total time spent learning
        - total_sessions: Total number of sessions
    """
    try:
        progress_repo = ProgressRepository(db_pool)
        progress = await progress_repo.get_user_progress(user_id)

        if not progress:
            # Create initial progress record
            progress = await progress_repo.create_or_get_progress(user_id)

        return ResponseSchema(
            success=True,
            data=dict(progress),
            message="User progress retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user progress: {str(e)}"
        )


@router.get("/{user_id}/stats", response_model=ResponseSchema)
async def get_user_statistics(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool),
):
    """Get comprehensive user statistics including session analytics.

    Includes all progress data plus:
        - avg_session_duration: Average session duration in seconds
        - Additional analytics from learning_sessions table
    """
    try:
        progress_repo = ProgressRepository(db_pool)
        stats = await progress_repo.get_user_statistics(user_id)

        return ResponseSchema(
            success=True,
            data=stats,
            message="User statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user statistics: {str(e)}"
        )


@router.post("/xp/add", response_model=ResponseSchema)
async def add_xp(
    request: AddXPRequest,
    db_pool: Pool = Depends(get_db_pool),
):
    """Add XP to user and automatically handle level-ups.

    The level system uses a power curve:
    - Level 1 → 2: 100 XP
    - Level 2 → 3: 200 XP
    - Level 3 → 4: 300 XP
    - etc.

    Maximum level is 100.

    Args:
        user_id: User to award XP to
        xp_amount: Amount of XP (1-10000)
        activity_type: Type of activity (for tracking)

    Returns:
        Updated progress record with new level if applicable
    """
    try:
        progress_repo = ProgressRepository(db_pool)
        updated_progress = await progress_repo.add_xp(
            user_id=request.user_id,
            xp_amount=request.xp_amount,
            activity_type=request.activity_type
        )

        # Update streak
        await progress_repo.update_streak(request.user_id)

        return ResponseSchema(
            success=True,
            data=dict(updated_progress),
            message=f"Added {request.xp_amount} XP. Current level: {updated_progress['current_level']}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding XP: {str(e)}"
        )


@router.post("/session/record", response_model=ResponseSchema)
async def record_session(
    request: RecordSessionRequest,
    db_pool: Pool = Depends(get_db_pool),
):
    """Record a completed learning session.

    Creates a learning session record and updates user's total statistics.
    Also automatically awards XP and updates streak.

    Session types:
    - conversation: Chat-based learning
    - grammar: Grammar rule practice
    - pronunciation: Pronunciation practice
    - review: Spaced repetition review

    Args:
        user_id: User who completed the session
        session_type: Type of learning session
        duration_seconds: How long the session lasted
        xp_earned: XP earned during the session

    Returns:
        Session record with updated progress
    """
    try:
        progress_repo = ProgressRepository(db_pool)

        # Record the session
        session = await progress_repo.record_session(
            user_id=request.user_id,
            session_type=request.session_type,
            duration_seconds=request.duration_seconds,
            xp_earned=request.xp_earned
        )

        # Add XP
        await progress_repo.add_xp(
            user_id=request.user_id,
            xp_amount=request.xp_earned,
            activity_type=request.session_type
        )

        # Update streak
        updated_progress = await progress_repo.update_streak(request.user_id)

        return ResponseSchema(
            success=True,
            data={
                "session": dict(session),
                "progress": dict(updated_progress)
            },
            message=f"Session recorded: {request.duration_seconds}s, {request.xp_earned} XP earned"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording session: {str(e)}"
        )


# Achievement endpoints

@router.get("/achievements/available", response_model=ResponseSchema)
async def get_available_achievements(
    db_pool: Pool = Depends(get_db_pool),
):
    """Get all available achievements that can be earned.

    Returns list of all active achievements with their descriptions,
    XP rewards, and difficulty tiers.

    Difficulty tiers:
    - bronze: Easy achievements
    - silver: Moderate achievements
    - gold: Difficult achievements
    - platinum: Very difficult/rare achievements
    """
    try:
        progress_repo = ProgressRepository(db_pool)
        achievements = await progress_repo.get_all_achievements()

        return ResponseSchema(
            success=True,
            data={"achievements": [dict(a) for a in achievements]},
            message=f"Retrieved {len(achievements)} available achievements"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching achievements: {str(e)}"
        )


@router.get("/achievements/{user_id}", response_model=ResponseSchema)
async def get_user_achievements(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool),
):
    """Get achievements earned by a specific user.

    Returns list of achievements the user has earned, including:
    - Achievement details
    - When it was earned
    - Context metadata (if available)
    """
    try:
        progress_repo = ProgressRepository(db_pool)
        achievements = await progress_repo.get_user_achievements(user_id)

        return ResponseSchema(
            success=True,
            data={"achievements": [dict(a) for a in achievements]},
            message=f"User has earned {len(achievements)} achievements"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user achievements: {str(e)}"
        )


@router.post("/achievements/award", response_model=ResponseSchema)
async def award_achievement(
    request: AwardAchievementRequest,
    db_pool: Pool = Depends(get_db_pool),
):
    """Award an achievement to a user.

    Automatically awards the associated XP reward.
    If user already has the achievement, this is a no-op.

    Args:
        user_id: User to award achievement to
        achievement_code: Code of achievement to award
        metadata: Optional context about how it was earned

    Returns:
        Achievement details if newly awarded, or notification if already had it
    """
    try:
        progress_repo = ProgressRepository(db_pool)
        achievement = await progress_repo.award_achievement(
            user_id=request.user_id,
            achievement_code=request.achievement_code,
            metadata=request.metadata
        )

        if not achievement:
            return ResponseSchema(
                success=True,
                data={"newly_awarded": False},
                message="User already has this achievement"
            )

        return ResponseSchema(
            success=True,
            data={
                "newly_awarded": True,
                "achievement": dict(achievement),
                "xp_awarded": achievement["xp_reward"]
            },
            message=f"Achievement '{achievement['title_en']}' awarded! +{achievement['xp_reward']} XP"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error awarding achievement: {str(e)}"
        )


@router.get("/leaderboard", response_model=ResponseSchema)
async def get_leaderboard(
    metric: str = Query("total_xp", description="Metric to rank by: total_xp, current_level, longest_streak, total_study_time_seconds"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    db_pool: Pool = Depends(get_db_pool),
):
    """Get leaderboard rankings.

    Returns top users ranked by selected metric.

    Available metrics:
    - total_xp: Total experience points
    - current_level: Current level
    - longest_streak: Longest daily streak
    - total_study_time_seconds: Total study time

    Args:
        metric: What to rank users by
        limit: How many users to return (max 1000)

    Returns:
        Ranked list of users with their stats
    """
    try:
        progress_repo = ProgressRepository(db_pool)
        leaderboard = await progress_repo.get_leaderboard(
            metric=metric,
            limit=limit
        )

        return ResponseSchema(
            success=True,
            data={
                "metric": metric,
                "entries": [dict(entry) for entry in leaderboard],
                "total_count": len(leaderboard)
            },
            message=f"Leaderboard retrieved: top {len(leaderboard)} users by {metric}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching leaderboard: {str(e)}"
        )
