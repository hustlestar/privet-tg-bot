"""Main FastAPI application for vocabulary learning API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import api_router
from src.database import init_pool, close_pool

app = FastAPI(
    title="Learn Words Vocabulary API",
    description="Vocabulary learning, translation, and training API for language learners",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # user-app
        "http://localhost:3001",  # admin-app
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database pool on startup."""
    await init_pool()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database pool on shutdown."""
    await close_pool()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "learn-words-api"}
