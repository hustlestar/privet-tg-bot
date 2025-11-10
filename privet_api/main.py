"""Main FastAPI application."""

import logging
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from privet_api.core.config import settings
from privet_api.core.database import DatabaseManager
from privet_api.repositories.user_repository import UserRepository
from privet_api.repositories.conversation_repository import ConversationRepository
from privet_api.repositories.fact_repository import FactRepository
from privet_api.repositories.profile_repository import ProfileRepository
from privet_api.repositories.api_usage_repository import APIUsageRepository
from privet_api.repositories.pronunciation_repository import PronunciationRepository
from privet_api.repositories.vocabulary_repository import VocabularyRepository
from privet_api.services.rag.rag_service import RAGService
from privet_api.services.audio.audio_service import AudioService
from privet_api.services.conversation.conversation_manager import ConversationManager
from privet_api.services.nlp.nlp_service import NLPService
from privet_api.services.ai.ai_provider import OpenRouterProvider, MockAIProvider
from privet_api.services.expense_tracker import ExpenseTracker
from privet_api.services.pronunciation.pronunciation_service import PronunciationService
from privet_api.services.vocabulary.vocabulary_service import VocabularyService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


# Database manager instance
db_manager: Optional[DatabaseManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global db_manager
    
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize database
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.setup()
    logger.info("Database initialized")
    
    # Register database manager for dependency injection
    from privet_api.api.deps import set_db_manager, set_service
    set_db_manager(db_manager)
    
    # Initialize repositories
    user_repo = UserRepository(db_manager.pool)
    conversation_repo = ConversationRepository(db_manager.pool)
    fact_repo = FactRepository(db_manager.pool)
    profile_repo = ProfileRepository(db_manager.pool)
    api_usage_repo = APIUsageRepository(db_manager.pool)
    pronunciation_repo = PronunciationRepository(db_manager.pool)
    vocabulary_repo = VocabularyRepository(db_manager.pool)
    
    # Initialize expense tracker
    expense_tracker = ExpenseTracker(api_usage_repo)
    logger.info("Expense tracker initialized")
    
    # Initialize AI provider
    if settings.openrouter_api_key:
        ai_provider = OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            expense_tracker=expense_tracker
        )
        logger.info(f"OpenRouter AI provider initialized with model: {settings.openrouter_model}")
    else:
        ai_provider = MockAIProvider()
        logger.warning("Using Mock AI provider - no OpenRouter API key configured")
    
    # Initialize services
    rag_service = RAGService(
        fact_repository=fact_repo,
        profile_repository=profile_repo,
        conversation_repository=conversation_repo,
        openai_api_key=settings.openai_api_key,
        embedding_model=settings.embedding_model,
        embedding_dimension=settings.embedding_dimension,
        similarity_threshold=settings.rag_similarity_threshold,
    )
    logger.info("RAG service initialized")
    
    audio_service = AudioService(
        openai_api_key=settings.openai_api_key,
        tts_provider=settings.tts_provider,
        tts_api_key=settings.openai_api_key if settings.tts_provider == "openai" else settings.elevenlabs_api_key,
        tts_voice=settings.tts_voice,
        tts_model=settings.tts_model,
    )
    logger.info(f"Audio service initialized with TTS provider: {settings.tts_provider}")
    
    nlp_service = NLPService()
    logger.info("NLP service initialized")
    
    conversation_manager = ConversationManager(
        user_repository=user_repo,
        conversation_repository=conversation_repo,
        fact_repository=fact_repo,
        profile_repository=profile_repo,
        rag_service=rag_service,
        ai_provider=ai_provider,
    )
    logger.info("Conversation manager initialized")

    # Initialize language learning services
    pronunciation_service = PronunciationService(
        audio_service=audio_service,
        pronunciation_repo=pronunciation_repo,
    )
    logger.info("Pronunciation service initialized")

    vocabulary_service = VocabularyService(
        vocabulary_repo=vocabulary_repo,
        pronunciation_service=pronunciation_service,
    )
    logger.info("Vocabulary service initialized")
    
    # Register services for dependency injection
    set_service("user_repository", user_repo)
    set_service("conversation_repository", conversation_repo)
    set_service("fact_repository", fact_repo)
    set_service("profile_repository", profile_repo)
    set_service("api_usage_repository", api_usage_repo)
    set_service("pronunciation_repository", pronunciation_repo)
    set_service("vocabulary_repository", vocabulary_repo)
    set_service("expense_tracker", expense_tracker)
    set_service("rag_service", rag_service)
    set_service("audio_service", audio_service)
    set_service("nlp_service", nlp_service)
    set_service("ai_provider", ai_provider)
    set_service("conversation_manager", conversation_manager)
    set_service("pronunciation_service", pronunciation_service)
    set_service("vocabulary_service", vocabulary_service)

    logger.info("All services initialized and registered")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    if db_manager:
        await db_manager.close()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip middleware for compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": "connected" if db_manager and db_manager.pool else "disconnected"
    }


# Include API router
from privet_api.api.v1.router import api_router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": "internal_server_error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Exclude directories from file watching to prevent crashes
    reload_excludes = [
        "*/node_modules/*",
        "*/.git/*",
        "*/__pycache__/*",
        "*.pyc",
        "*/.venv/*",
        "*/.env",
        "*/privet-ui/*",  # Exclude the entire UI directory
    ]
    
    uvicorn.run(
        "privet_api.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        reload_excludes=reload_excludes if settings.debug else None,
        log_level=settings.log_level.lower(),
    )