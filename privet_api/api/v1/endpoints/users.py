"""User management endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from asyncpg import Pool

from privet_api.api.deps import get_db_pool
from privet_api.models.schemas.user import (
    User, UserCreate, UserUpdate, UserStats
)
from privet_api.models.schemas.base import PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    db_pool: Pool = Depends(get_db_pool)
) -> User:
    """Create a new user."""
    
    async with db_pool.acquire() as conn:
        # Check if user already exists
        existing = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_data.user_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with ID {user_data.user_id} already exists"
            )
        
        # Create user (matching actual schema)
        user = await conn.fetchrow(
            """
            INSERT INTO users (user_id, username, language, created_at)
            VALUES ($1, $2, $3, NOW())
            RETURNING *
            """,
            user_data.user_id,
            user_data.username or f"user_{user_data.user_id}",
            user_data.language
        )
        
        return User(**dict(user))


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool)
) -> User:
    """Get user by ID."""
    
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        return User(**dict(user))


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db_pool: Pool = Depends(get_db_pool)
) -> User:
    """Update user information."""
    
    async with db_pool.acquire() as conn:
        # Check if user exists
        existing = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Build update query dynamically
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in user_data.model_dump(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_count}")
            values.append(value)
            param_count += 1
        
        if not update_fields:
            return User(**dict(existing))
        
        # Add updated_at
        update_fields.append(f"updated_at = ${param_count}")
        values.append("NOW()")
        param_count += 1
        
        # Add user_id for WHERE clause
        values.append(user_id)
        
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE user_id = ${param_count}
            RETURNING *
        """
        
        user = await conn.fetchrow(query, *values)
        return User(**dict(user))


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool)
) -> dict:
    """Delete a user and all associated data."""
    
    async with db_pool.acquire() as conn:
        # Start transaction
        async with conn.transaction():
            # Check if user exists
            existing = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1",
                user_id
            )
            
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )
            
            # Delete in order of dependencies
            await conn.execute("DELETE FROM user_facts WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM user_profile_summaries WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM conversation_messages WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM users WHERE user_id = $1", user_id)
        
        return {"message": f"User {user_id} and all associated data deleted successfully"}


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool)
) -> UserStats:
    """Get user statistics."""
    
    async with db_pool.acquire() as conn:
        # Check if user exists
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Get statistics
        message_count = await conn.fetchval(
            "SELECT COUNT(*) FROM conversation_messages WHERE user_id = $1",
            user_id
        )
        
        voice_count = await conn.fetchval(
            "SELECT COUNT(*) FROM conversation_messages WHERE user_id = $1 AND transcribed_text IS NOT NULL",
            user_id
        )
        
        facts_count = await conn.fetchval(
            "SELECT COUNT(*) FROM user_facts WHERE user_id = $1",
            user_id
        )
        
        summaries_count = await conn.fetchval(
            "SELECT COUNT(*) FROM user_profile_summaries WHERE user_id = $1",
            user_id
        )
        
        last_message = await conn.fetchval(
            "SELECT MAX(created_at) FROM conversation_messages WHERE user_id = $1",
            user_id
        )
        
        # Calculate memory density
        memory_density = facts_count / max(message_count, 1)
        
        return UserStats(
            user_id=user_id,
            total_messages=message_count or 0,
            total_voice_messages=voice_count or 0,
            total_facts=facts_count or 0,
            profile_summaries=summaries_count or 0,
            memory_density=memory_density,
            last_active=last_message
        )


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db_pool: Pool = Depends(get_db_pool)
) -> PaginatedResponse:
    """List all users with pagination."""
    
    async with db_pool.acquire() as conn:
        # Get total count
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        # Get users
        users = await conn.fetch(
            """
            SELECT * FROM users 
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset
        )
        
        return PaginatedResponse(
            items=[User(**dict(user)) for user in users],
            total=total or 0,
            offset=offset,
            limit=limit
        )