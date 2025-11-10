"""API dependencies for dependency injection."""

from typing import Generator, Optional, Annotated
from fastapi import Depends, HTTPException, Header, status
from asyncpg import Pool

from privet_api.core.config import settings
from privet_api.core.database import DatabaseManager


# Global instances (will be initialized in main.py)
_db_manager: Optional[DatabaseManager] = None
_services = {}


def set_db_manager(db_manager: DatabaseManager):
    """Set the global database manager instance."""
    global _db_manager
    _db_manager = db_manager


def set_service(name: str, service):
    """Register a service for dependency injection."""
    global _services
    _services[name] = service


def get_service(name: str):
    """Get a registered service."""
    return _services.get(name)


async def get_db_pool() -> Pool:
    """Get database connection pool."""
    if not _db_manager or not _db_manager.pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    return _db_manager.pool


async def get_db_manager() -> DatabaseManager:
    """Get database manager instance."""
    if not _db_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database manager not available"
        )
    return _db_manager


async def verify_api_key(
    api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None
) -> str:
    """Verify API key from header."""
    # For now, we'll implement a simple check
    # In production, this should validate against a database or cache
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # TODO: Implement proper API key validation
    # For now, accept any non-empty key
    return api_key


async def get_current_user_id(
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Optional[int] = Header(None, alias="X-User-ID")
) -> Optional[int]:
    """Get current user ID from headers."""
    return user_id


# Service dependencies (to be implemented as services are moved)

async def get_rag_service():
    """Get RAG service instance."""
    service = get_service("rag_service")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service not available"
        )
    return service


async def get_conversation_manager():
    """Get conversation manager instance."""
    service = get_service("conversation_manager")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conversation manager not available"
        )
    return service


async def get_audio_service():
    """Get audio service instance."""
    service = get_service("audio_service")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audio service not available"
        )
    return service


async def get_ai_provider():
    """Get AI provider instance."""
    service = get_service("ai_provider")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI provider not available"
        )
    return service


async def get_nlp_service():
    """Get NLP service instance."""
    service = get_service("nlp_service")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP service not available"
        )
    return service


# Repository dependencies

async def get_user_repository():
    """Get user repository instance."""
    repo = get_service("user_repository")
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User repository not available"
        )
    return repo


async def get_conversation_repository():
    """Get conversation repository instance."""
    repo = get_service("conversation_repository")
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conversation repository not available"
        )
    return repo


async def get_fact_repository():
    """Get fact repository instance."""
    repo = get_service("fact_repository")
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fact repository not available"
        )
    return repo


async def get_profile_repository():
    """Get profile repository instance."""
    repo = get_service("profile_repository")
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile repository not available"
        )
    return repo


async def get_api_usage_repository():
    """Get API usage repository instance."""
    repo = get_service("api_usage_repository")
    if not repo:
        # Create a new instance if not available
        from privet_api.repositories.api_usage_repository import APIUsageRepository
        pool = await get_db_pool()
        repo = APIUsageRepository(pool)
        set_service("api_usage_repository", repo)
    return repo


# Language Learning Dependencies

async def get_pronunciation_repository():
    """Get pronunciation repository instance."""
    repo = get_service("pronunciation_repository")
    if not repo:
        from privet_api.repositories.pronunciation_repository import PronunciationRepository
        pool = await get_db_pool()
        repo = PronunciationRepository(pool)
        set_service("pronunciation_repository", repo)
    return repo


async def get_pronunciation_service():
    """Get pronunciation service instance."""
    service = get_service("pronunciation_service")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pronunciation service not available"
        )
    return service