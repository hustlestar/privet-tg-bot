"""Main API v1 router."""

from fastapi import APIRouter
from privet_api.api.v1.endpoints import (
    users,
    conversations,
    voice,
    memory,
    health,
    expenses
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])