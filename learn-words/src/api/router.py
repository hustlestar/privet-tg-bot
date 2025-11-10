"""Main API router combining all endpoints."""

from fastapi import APIRouter
from src.api.endpoints import (
    translation_router,
    vocabulary_router,
    training_router,
    users_router,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(translation_router)
api_router.include_router(vocabulary_router)
api_router.include_router(training_router)
api_router.include_router(users_router)
