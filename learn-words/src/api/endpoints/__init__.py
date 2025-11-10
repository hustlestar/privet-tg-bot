"""API endpoint routers."""

from .translation import router as translation_router
from .vocabulary import router as vocabulary_router
from .training import router as training_router
from .users import router as users_router

__all__ = [
    "translation_router",
    "vocabulary_router",
    "training_router",
    "users_router",
]
