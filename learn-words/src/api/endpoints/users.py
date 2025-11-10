"""User management API endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from src.dao.user_dao import UserDao
from src.dao.models import User, ResponseMode, ExplanationLanguage, UserPlan
from src.api.deps import get_pool
from src.api.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserStatsResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreateRequest, pool=Depends(get_pool)):
    """Create a new user profile."""
    try:
        user_dao = UserDao(pool)

        # Convert string enums to enum objects
        response_mode = ResponseMode(request.response_mode)
        explanation_language = ExplanationLanguage(request.explanation_language)
        plan = UserPlan(request.plan)

        # Create user object
        user = User(
            user_id=request.user_id,
            learning_language=request.learning_language.lower(),
            interface_language=request.interface_language,
            response_mode=response_mode,
            explanation_language=explanation_language,
            plan=plan,
            timezone=request.timezone,
            notification_times=request.notification_times or [],
            notification_times_count=len(request.notification_times) if request.notification_times else 0,
            telegram_handle=request.telegram_handle,
        )

        # Create user in database
        await user_dao.create_user(user)

        # Fetch and return created user
        created_user = await user_dao.get_user(request.user_id)

        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but could not be retrieved",
            )

        return UserResponse(
            user_id=created_user.user_id,
            learning_language=created_user.learning_language,
            interface_language=created_user.interface_language,
            response_mode=created_user.response_mode.value,
            explanation_language=created_user.explanation_language.value,
            plan=created_user.plan.value,
            timezone=created_user.timezone,
            notification_times=created_user.notification_times or [],
            notification_times_count=created_user.notification_times_count,
            created_at=created_user.created_at,
            is_blocked=created_user.is_blocked,
            telegram_handle=created_user.telegram_handle,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, pool=Depends(get_pool)):
    """Get user profile by ID."""
    try:
        user_dao = UserDao(pool)
        user = await user_dao.get_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        return UserResponse(
            user_id=user.user_id,
            learning_language=user.learning_language,
            interface_language=user.interface_language,
            response_mode=user.response_mode.value,
            explanation_language=user.explanation_language.value,
            plan=user.plan.value,
            timezone=user.timezone,
            notification_times=user.notification_times or [],
            notification_times_count=user.notification_times_count,
            created_at=user.created_at,
            is_blocked=user.is_blocked,
            telegram_handle=user.telegram_handle,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}",
        )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, request: UserUpdateRequest, pool=Depends(get_pool)
):
    """Update user profile settings."""
    try:
        user_dao = UserDao(pool)

        # Get current user
        current_user = await user_dao.get_user(user_id)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        # Update only provided fields
        if request.learning_language is not None:
            current_user.learning_language = request.learning_language.lower()
        if request.interface_language is not None:
            current_user.interface_language = request.interface_language
        if request.response_mode is not None:
            current_user.response_mode = ResponseMode(request.response_mode)
        if request.explanation_language is not None:
            current_user.explanation_language = ExplanationLanguage(
                request.explanation_language
            )
        if request.plan is not None:
            current_user.plan = UserPlan(request.plan)
        if request.timezone is not None:
            current_user.timezone = request.timezone
        if request.notification_times is not None:
            current_user.notification_times = request.notification_times
            current_user.notification_times_count = len(request.notification_times)

        # Save updates
        await user_dao.update_user(current_user)

        # Fetch and return updated user
        updated_user = await user_dao.get_user(user_id)

        return UserResponse(
            user_id=updated_user.user_id,
            learning_language=updated_user.learning_language,
            interface_language=updated_user.interface_language,
            response_mode=updated_user.response_mode.value,
            explanation_language=updated_user.explanation_language.value,
            plan=updated_user.plan.value,
            timezone=updated_user.timezone,
            notification_times=updated_user.notification_times or [],
            notification_times_count=updated_user.notification_times_count,
            created_at=updated_user.created_at,
            is_blocked=updated_user.is_blocked,
            telegram_handle=updated_user.telegram_handle,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}",
        )


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: int, pool=Depends(get_pool)):
    """Get comprehensive user statistics."""
    try:
        user_dao = UserDao(pool)
        stats = await user_dao.get_user_stats(user_id)

        # Calculate success rates
        success_rate = (
            stats["total_correct"] / stats["total_attempts"]
            if stats["total_attempts"] > 0
            else 0.0
        )

        recent_success_rate = (
            stats["recent_correct"] / stats["recent_attempts"]
            if stats["recent_attempts"] > 0
            else 0.0
        )

        return UserStatsResponse(
            user_id=user_id,
            total_words=stats["total_words"],
            known_words=stats["known_words"],
            learning_words=stats["total_words"] - stats["known_words"],
            total_attempts=stats["total_attempts"],
            total_correct=stats["total_correct"],
            success_rate=success_rate,
            recent_attempts=stats["recent_attempts"],
            recent_correct=stats["recent_correct"],
            recent_success_rate=recent_success_rate,
            current_streak=0,  # TODO: implement streak calculation
            last_activity=None,  # TODO: implement last activity tracking
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}",
        )


@router.get("/", response_model=list[UserResponse])
async def get_all_users(pool=Depends(get_pool)):
    """Get all users (admin endpoint)."""
    try:
        user_dao = UserDao(pool)
        users = await user_dao.get_all_users()

        return [
            UserResponse(
                user_id=user.user_id,
                learning_language=user.learning_language,
                interface_language=user.interface_language,
                response_mode=user.response_mode.value,
                explanation_language=user.explanation_language.value,
                plan=user.plan.value,
                timezone=user.timezone,
                notification_times=user.notification_times or [],
                notification_times_count=user.notification_times_count,
                created_at=user.created_at,
                is_blocked=user.is_blocked,
                telegram_handle=user.telegram_handle,
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}",
        )
