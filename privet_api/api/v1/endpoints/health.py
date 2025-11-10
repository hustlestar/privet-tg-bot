"""Health check endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from asyncpg import Pool

from privet_api.api.deps import get_db_pool
from privet_api.core.config import settings

router = APIRouter()


@router.get("/status")
async def health_status() -> Dict[str, Any]:
    """Get API health status."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": "production" if not settings.debug else "development"
    }


@router.get("/ready")
async def readiness_check(
    db_pool: Pool = Depends(get_db_pool)
) -> Dict[str, Any]:
    """Check if the API is ready to handle requests."""
    
    # Check database connection
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check services (will be expanded as services are added)
    services_status = {
        "database": db_status,
        "rag_service": "not_initialized",  # TODO: Check actual service
        "audio_service": "not_initialized",  # TODO: Check actual service
        "ai_provider": "not_initialized",  # TODO: Check actual service
    }
    
    all_healthy = all(
        status == "connected" or status == "initialized" 
        for status in services_status.values()
    )
    
    return {
        "ready": all_healthy,
        "services": services_status
    }


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Simple liveness check."""
    return {"status": "alive"}