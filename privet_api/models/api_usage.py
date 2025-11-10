"""API Usage tracking model."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class APIUsage(Base):
    """Track API usage and costs for different models and services."""
    
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)  # Optional user association
    service_type = Column(String(50), nullable=False)  # 'llm', 'embedding', 'tts', 'stt'
    provider = Column(String(50), nullable=False)  # 'openrouter', 'openai', etc.
    model = Column(String(100), nullable=False)  # Model name used
    
    # Token usage
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # Cost information
    prompt_cost = Column(Float, nullable=True)  # Cost for input tokens
    completion_cost = Column(Float, nullable=True)  # Cost for output tokens
    total_cost = Column(Float, nullable=False, default=0.0)  # Total cost in USD
    
    # Request metadata
    request_type = Column(String(50), nullable=True)  # 'chat', 'completion', 'embedding'
    input_length = Column(Integer, nullable=True)  # Length of input text/audio
    output_length = Column(Integer, nullable=True)  # Length of output text/audio
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)  # Extra data like temperature, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<APIUsage(id={self.id}, service={self.service_type}, provider={self.provider}, model={self.model}, cost=${self.total_cost:.4f})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "service_type": self.service_type,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "prompt_cost": self.prompt_cost,
            "completion_cost": self.completion_cost,
            "total_cost": self.total_cost,
            "request_type": self.request_type,
            "input_length": self.input_length,
            "output_length": self.output_length,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }