"""Configuration for the FastAPI application."""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    app_name: str = "Privet API"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    # Security
    api_key_header: str = "X-API-Key"
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = Field(default=30, env="JWT_EXPIRATION_MINUTES")
    
    # AI Services
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="google/gemini-2.0-flash-001", env="OPENROUTER_MODEL")
    elevenlabs_api_key: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    
    # TTS Configuration
    tts_provider: str = Field(default="openai", env="TTS_PROVIDER")
    tts_voice: str = Field(default="nova", env="TTS_VOICE")
    tts_model: str = Field(default="tts-1", env="TTS_MODEL")
    
    # RAG Configuration
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, env="EMBEDDING_DIMENSION")
    rag_similarity_threshold: float = Field(default=0.7, env="RAG_SIMILARITY_THRESHOLD")
    
    # Redis Cache (optional)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # File Storage
    upload_max_size_mb: int = Field(default=25, env="UPLOAD_MAX_SIZE_MB")
    audio_storage_path: str = Field(default="/tmp/privet_audio", env="AUDIO_STORAGE_PATH")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env
        
    @property
    def upload_max_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.upload_max_size_mb * 1024 * 1024
    
    @property
    def database_url_asyncpg(self) -> str:
        """Convert database URL for asyncpg."""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url


settings = Settings()