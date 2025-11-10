"""Factory for creating TTS providers."""

import logging
from typing import Optional

from .tts_base import BaseTTSProvider

logger = logging.getLogger(__name__)


class TTSFactory:
    """Factory for creating TTS provider instances."""
    
    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        language: str = "en",
        model: Optional[str] = None,
    ) -> BaseTTSProvider:
        """Create a TTS provider instance.
        
        Args:
            provider_name: Name of the provider (openai, elevenlabs, google, amazon)
            api_key: API key for the service
            voice_id: Default voice ID
            language: Default language
            model: Model to use (provider-specific)
            
        Returns:
            TTS provider instance
            
        Raises:
            ValueError: If provider name is not supported
        """
        provider_name = provider_name.lower()
        
        if provider_name == "openai":
            from .openai_provider import OpenAITTSProvider
            return OpenAITTSProvider(
                api_key=api_key,
                voice_id=voice_id or "nova",
                language=language,
                model=model or "tts-1",
            )
        elif provider_name == "elevenlabs":
            from .elevenlabs_provider import ElevenLabsProvider
            return ElevenLabsProvider(
                api_key=api_key,
                voice_id=voice_id or "EXAVITQu4vr4xnSDxMaL",  # Default Sarah voice
                language=language,
                model=model or "eleven_multilingual_v2",
            )
        elif provider_name == "google":
            from .google_provider import GoogleTTSProvider
            return GoogleTTSProvider(
                api_key=api_key,
                voice_id=voice_id or "en-US-Neural2-F",
                language=language or "en-US",
            )
        elif provider_name == "amazon":
            from .amazon_provider import AmazonPollyProvider
            return AmazonPollyProvider(
                api_key=api_key,
                voice_id=voice_id or "Joanna",
                language=language or "en-US",
            )
        else:
            raise ValueError(f"Unsupported TTS provider: {provider_name}")
    
    @staticmethod
    def from_env(
        provider_name: Optional[str] = None,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
        model: Optional[str] = None,
    ) -> BaseTTSProvider:
        """Create TTS provider from environment variables.
        
        Args:
            provider_name: Override provider name
            voice_id: Override voice ID
            language: Override language
            model: Override model
            
        Returns:
            TTS provider instance
        """
        import os
        
        # Get provider name from env if not provided
        if not provider_name:
            provider_name = os.getenv("TTS_PROVIDER", "openai")
        
        # Get API key based on provider
        api_key = None
        if provider_name == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider_name == "elevenlabs":
            api_key = os.getenv("ELEVENLABS_API_KEY")
        elif provider_name == "google":
            api_key = os.getenv("GOOGLE_TTS_API_KEY")
        elif provider_name == "amazon":
            api_key = os.getenv("AMAZON_POLLY_API_KEY")
        
        # Get other settings from env
        if not voice_id:
            voice_id = os.getenv("TTS_VOICE")
        if not language:
            language = os.getenv("TTS_LANGUAGE", "en")
        if not model:
            model = os.getenv("TTS_MODEL")
        
        return TTSFactory.create_provider(
            provider_name=provider_name,
            api_key=api_key,
            voice_id=voice_id,
            language=language,
            model=model,
        )