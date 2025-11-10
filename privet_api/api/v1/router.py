"""Main API v1 router."""

from fastapi import APIRouter
from privet_api.api.v1.endpoints import (
    users,
    conversations,
    voice,
    memory,
    health,
    expenses,
    pronunciation,
    streaming,
    grammar,
    progress,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(pronunciation.router, prefix="/pronunciation", tags=["pronunciation"])
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
api_router.include_router(grammar.router, prefix="/grammar", tags=["grammar"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])