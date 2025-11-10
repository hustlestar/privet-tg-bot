"""Python client for the Privet API."""

import asyncio
from typing import Optional, Dict, Any, List, BinaryIO
from pathlib import Path
import httpx
import base64
from contextlib import asynccontextmanager

from privet_api.models.schemas.user import User, UserCreate, UserUpdate, UserStats
from privet_api.models.schemas.conversation import (
    ConversationRequest, ConversationResponse, ConversationHistory, EmotionAnalysis
)
from privet_api.models.schemas.voice import (
    TranscriptionResponse, SynthesisRequest, SynthesisResponse,
    VoiceProcessingResponse, TTSProvider
)
from privet_api.models.schemas.memory import (
    FactCreate, FactSearch, FactSearchResult, ProfileSummary,
    ProfileSummaryCreate, MemoryContext, MemoryStats
)


class PrivetAPIClient:
    """Async client for interacting with the Privet API."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """Initialize the API client.
        
        Args:
            base_url: Base URL of the API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "default-api-key"  # TODO: Implement proper key management
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
    
    @asynccontextmanager
    async def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=self.timeout,
                follow_redirects=True  # Handle trailing slash redirects
            )
        try:
            yield self._client
        finally:
            pass  # Keep client alive for reuse
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> httpx.Response:
        """Make an HTTP request with retry logic."""
        url = f"{endpoint}" if endpoint.startswith("/") else f"/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self._get_client() as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        json=json_data,
                        params=params,
                        files=files,
                        headers=headers
                    )
                    response.raise_for_status()
                    return response
                    
            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
    
    # Health endpoints
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = await self._request("GET", "/health")
        return response.json()
    
    async def readiness_check(self) -> Dict[str, Any]:
        """Check if API is ready."""
        response = await self._request("GET", "/api/v1/health/ready")
        return response.json()
    
    # User endpoints
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        response = await self._request(
            "POST",
            "/api/v1/users",
            json_data=user_data.model_dump()
        )
        return User(**response.json())
    
    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        response = await self._request("GET", f"/api/v1/users/{user_id}")
        return User(**response.json())
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information."""
        response = await self._request(
            "PUT",
            f"/api/v1/users/{user_id}",
            json_data=user_data.model_dump(exclude_unset=True)
        )
        return User(**response.json())
    
    async def delete_user(self, user_id: int) -> Dict[str, str]:
        """Delete a user."""
        response = await self._request("DELETE", f"/api/v1/users/{user_id}")
        return response.json()
    
    async def get_user_stats(self, user_id: int) -> UserStats:
        """Get user statistics."""
        response = await self._request("GET", f"/api/v1/users/{user_id}/stats")
        return UserStats(**response.json())
    
    # Conversation endpoints
    
    async def process_conversation(
        self,
        user_id: int,
        message: str,
        is_voice: bool = False,
        context: Optional[Dict] = None
    ) -> ConversationResponse:
        """Process a conversation message."""
        request = ConversationRequest(
            user_id=user_id,
            message=message,
            is_voice=is_voice,
            context=context
        )
        response = await self._request(
            "POST",
            "/api/v1/conversations/process",
            json_data=request.model_dump()
        )
        return ConversationResponse(**response.json())
    
    async def get_conversation_history(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> ConversationHistory:
        """Get conversation history for a user."""
        response = await self._request(
            "GET",
            f"/api/v1/conversations/{user_id}/history",
            params={"limit": limit, "offset": offset}
        )
        return ConversationHistory(**response.json())
    
    async def analyze_emotion(self, user_id: int, text: str) -> EmotionAnalysis:
        """Analyze emotion in text."""
        response = await self._request(
            "POST",
            f"/api/v1/conversations/{user_id}/analyze-emotion",
            params={"text": text}
        )
        return EmotionAnalysis(**response.json())
    
    # Voice endpoints
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        user_id: Optional[int] = None,
        language: Optional[str] = None
    ) -> TranscriptionResponse:
        """Transcribe audio to text."""
        files = {
            "audio_file": ("audio.ogg", audio_data, "audio/ogg")
        }
        data = {}
        if user_id:
            data["user_id"] = str(user_id)
        if language:
            data["language"] = language
            
        response = await self._request(
            "POST",
            "/api/v1/voice/transcribe",
            files=files,
            headers={"X-API-Key": self.api_key}  # Override content-type for multipart
        )
        return TranscriptionResponse(**response.json())
    
    async def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        speed: float = 1.0
    ) -> bytes:
        """Synthesize text to speech."""
        request = SynthesisRequest(
            text=text,
            voice=voice,
            emotion=emotion,
            speed=speed
        )
        response = await self._request(
            "POST",
            "/api/v1/voice/synthesize",
            json_data=request.model_dump()
        )
        data = response.json()
        synthesis_response = SynthesisResponse(**data)
        
        # Decode base64 audio
        if synthesis_response.audio_base64:
            return base64.b64decode(synthesis_response.audio_base64)
        elif synthesis_response.audio_url:
            # Download from URL
            async with self._get_client() as client:
                audio_response = await client.get(synthesis_response.audio_url)
                return audio_response.content
        else:
            raise ValueError("No audio data in response")
    
    async def process_voice_message(
        self,
        user_id: int,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> VoiceProcessingResponse:
        """Complete voice processing pipeline."""
        files = {
            "audio_file": ("audio.ogg", audio_data, "audio/ogg")
        }
        data = {"user_id": str(user_id)}
        if language:
            data["language"] = language
            
        response = await self._request(
            "POST",
            "/api/v1/voice/process",
            files=files,
            headers={"X-API-Key": self.api_key}
        )
        return VoiceProcessingResponse(**response.json())
    
    async def get_tts_providers(self) -> List[TTSProvider]:
        """Get available TTS providers."""
        response = await self._request("GET", "/api/v1/voice/providers")
        return [TTSProvider(**provider) for provider in response.json()]
    
    # Memory endpoints
    
    async def create_fact(
        self,
        user_id: int,
        fact_text: str,
        fact_summary: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store a new fact."""
        fact = FactCreate(
            user_id=user_id,
            fact_text=fact_text,
            fact_summary=fact_summary,
            category=category
        )
        response = await self._request(
            "POST",
            "/api/v1/memory/facts",
            json_data=fact.model_dump()
        )
        return response.json()
    
    async def search_facts(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[FactSearchResult]:
        """Search for relevant facts."""
        search = FactSearch(
            user_id=user_id,
            query=query,
            limit=limit,
            min_similarity=min_similarity
        )
        response = await self._request(
            "POST",
            "/api/v1/memory/facts/search",
            json_data=search.model_dump()
        )
        return [FactSearchResult(**fact) for fact in response.json()]
    
    async def generate_profile_summary(
        self,
        user_id: int,
        topic: str = "general",
        force_regenerate: bool = False
    ) -> ProfileSummary:
        """Generate or update user profile summary."""
        request = ProfileSummaryCreate(
            user_id=user_id,
            summary_topic=topic,
            force_regenerate=force_regenerate
        )
        response = await self._request(
            "POST",
            "/api/v1/memory/summaries/generate",
            json_data=request.model_dump()
        )
        return ProfileSummary(**response.json())
    
    async def get_memory_context(
        self,
        user_id: int,
        query: Optional[str] = None
    ) -> MemoryContext:
        """Get complete memory context for a user."""
        params = {"query": query} if query else {}
        response = await self._request(
            "GET",
            f"/api/v1/memory/context/{user_id}",
            params=params
        )
        return MemoryContext(**response.json())
    
    async def get_memory_stats(self, user_id: int) -> MemoryStats:
        """Get memory statistics for a user."""
        response = await self._request("GET", f"/api/v1/memory/stats/{user_id}")
        return MemoryStats(**response.json())


# Convenience function for creating a client
def create_client(
    base_url: str = "http://localhost:8000",
    api_key: Optional[str] = None
) -> PrivetAPIClient:
    """Create a new API client instance."""
    return PrivetAPIClient(base_url=base_url, api_key=api_key)