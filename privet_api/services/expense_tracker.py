"""Expense tracking service for API calls."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from privet_api.repositories.api_usage_repository import APIUsageRepository

logger = logging.getLogger(__name__)


class ExpenseTracker:
    """Service for tracking API expenses and usage."""
    
    # Model pricing per 1M tokens (input/output) in USD
    MODEL_PRICING = {
        # OpenRouter models
        "google/gemini-2.0-flash-001": {"input": 0.075, "output": 0.30},
        "openai/gpt-4": {"input": 30.0, "output": 60.0},
        "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "openai/gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "anthropic/claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
        
        # OpenAI embeddings (per 1M tokens)
        "text-embedding-3-small": {"input": 0.02, "output": 0.0},
        "text-embedding-3-large": {"input": 0.13, "output": 0.0},
        "text-embedding-ada-002": {"input": 0.10, "output": 0.0},
        
        # TTS/STT pricing (per minute/hour)
        "tts-1": {"per_char": 0.000015},  # $15 per 1M characters
        "tts-1-hd": {"per_char": 0.00003},  # $30 per 1M characters
        "whisper-1": {"per_minute": 0.006},  # $0.006 per minute
    }
    
    def __init__(self, usage_repository: APIUsageRepository):
        self.usage_repo = usage_repository
        logger.info("ExpenseTracker initialized")
    
    def calculate_cost(
        self, 
        model: str, 
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        input_length: Optional[int] = None,
        duration_minutes: Optional[float] = None,
        service_type: str = "llm"
    ) -> Dict[str, float]:
        """Calculate cost for API usage.
        
        Args:
            model: Model name
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens  
            input_length: Length of input (for character-based pricing)
            duration_minutes: Duration in minutes (for time-based pricing)
            service_type: Type of service (llm, embedding, tts, stt)
            
        Returns:
            Dict with cost breakdown
        """
        if model not in self.MODEL_PRICING:
            logger.warning(f"No pricing data for model: {model}")
            return {"prompt_cost": 0.0, "completion_cost": 0.0, "total_cost": 0.0}
        
        pricing = self.MODEL_PRICING[model]
        prompt_cost = 0.0
        completion_cost = 0.0
        
        if service_type in ["llm", "embedding"] and prompt_tokens:
            # Token-based pricing (per 1M tokens)
            prompt_cost = (prompt_tokens / 1_000_000) * pricing.get("input", 0.0)
            
            if completion_tokens and "output" in pricing:
                completion_cost = (completion_tokens / 1_000_000) * pricing["output"]
        
        elif service_type == "tts" and input_length:
            # Character-based pricing for TTS
            prompt_cost = input_length * pricing.get("per_char", 0.0)
        
        elif service_type == "stt" and duration_minutes:
            # Time-based pricing for STT
            prompt_cost = duration_minutes * pricing.get("per_minute", 0.0)
        
        total_cost = prompt_cost + completion_cost
        
        return {
            "prompt_cost": round(prompt_cost, 6),
            "completion_cost": round(completion_cost, 6),
            "total_cost": round(total_cost, 6)
        }
    
    async def track_llm_usage(
        self,
        user_id: Optional[int],
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: Optional[int] = None,
        request_type: str = "chat",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track LLM API usage and calculate costs."""
        
        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens
        
        # Calculate costs
        costs = self.calculate_cost(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            service_type="llm"
        )
        
        # Store usage record
        try:
            record = await self.usage_repo.create_usage_record(
                user_id=user_id,
                service_type="llm",
                provider=provider,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                prompt_cost=costs["prompt_cost"],
                completion_cost=costs["completion_cost"],
                total_cost=costs["total_cost"],
                request_type=request_type,
                metadata=metadata
            )
            
            logger.info(
                f"LLM usage tracked: {provider}/{model} - "
                f"User: {user_id}, Tokens: {total_tokens}, Cost: ${costs['total_cost']:.4f}"
            )
            
            return record
            
        except Exception as e:
            logger.error(f"Failed to track LLM usage: {e}")
            return {}
    
    async def track_embedding_usage(
        self,
        user_id: Optional[int],
        provider: str,
        model: str,
        input_tokens: int,
        input_length: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track embedding API usage and calculate costs."""
        
        # Calculate costs
        costs = self.calculate_cost(
            model=model,
            prompt_tokens=input_tokens,
            service_type="embedding"
        )
        
        # Store usage record
        try:
            record = await self.usage_repo.create_usage_record(
                user_id=user_id,
                service_type="embedding",
                provider=provider,
                model=model,
                prompt_tokens=input_tokens,
                total_tokens=input_tokens,
                prompt_cost=costs["prompt_cost"],
                total_cost=costs["total_cost"],
                request_type="embedding",
                input_length=input_length,
                metadata=metadata
            )
            
            logger.info(
                f"Embedding usage tracked: {provider}/{model} - "
                f"User: {user_id}, Tokens: {input_tokens}, Cost: ${costs['total_cost']:.4f}"
            )
            
            return record
            
        except Exception as e:
            logger.error(f"Failed to track embedding usage: {e}")
            return {}
    
    async def track_tts_usage(
        self,
        user_id: Optional[int],
        provider: str,
        model: str,
        input_length: int,
        output_length: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track TTS API usage and calculate costs."""
        
        # Calculate costs based on character count
        costs = self.calculate_cost(
            model=model,
            input_length=input_length,
            service_type="tts"
        )
        
        # Store usage record
        try:
            record = await self.usage_repo.create_usage_record(
                user_id=user_id,
                service_type="tts",
                provider=provider,
                model=model,
                prompt_cost=costs["prompt_cost"],
                total_cost=costs["total_cost"],
                request_type="synthesis",
                input_length=input_length,
                output_length=output_length,
                metadata=metadata
            )
            
            logger.info(
                f"TTS usage tracked: {provider}/{model} - "
                f"User: {user_id}, Chars: {input_length}, Cost: ${costs['total_cost']:.4f}"
            )
            
            return record
            
        except Exception as e:
            logger.error(f"Failed to track TTS usage: {e}")
            return {}
    
    async def track_stt_usage(
        self,
        user_id: Optional[int],
        provider: str,
        model: str,
        duration_minutes: float,
        input_length: Optional[int] = None,
        output_length: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track STT API usage and calculate costs."""
        
        # Calculate costs based on duration
        costs = self.calculate_cost(
            model=model,
            duration_minutes=duration_minutes,
            service_type="stt"
        )
        
        # Store usage record
        try:
            record = await self.usage_repo.create_usage_record(
                user_id=user_id,
                service_type="stt",
                provider=provider,
                model=model,
                prompt_cost=costs["prompt_cost"],
                total_cost=costs["total_cost"],
                request_type="transcription",
                input_length=input_length,
                output_length=output_length,
                metadata=metadata
            )
            
            logger.info(
                f"STT usage tracked: {provider}/{model} - "
                f"User: {user_id}, Duration: {duration_minutes:.2f}min, Cost: ${costs['total_cost']:.4f}"
            )
            
            return record
            
        except Exception as e:
            logger.error(f"Failed to track STT usage: {e}")
            return {}