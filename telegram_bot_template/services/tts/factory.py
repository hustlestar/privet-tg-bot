"""TTS provider factory."""

import logging
from typing import Optional

from .base import TTSProvider, TTSConfig, BaseTTSProvider
from .elevenlabs_provider import ElevenLabsProvider
from .google_provider import GoogleTTSProvider
from .openai_provider import OpenAITTSProvider
from .amazon_provider import AmazonPollyProvider

logger = logging.getLogger(__name__)


class TTSFactory:
    """Factory for creating TTS providers."""
    
    @staticmethod
    def create_provider(config: TTSConfig) -> BaseTTSProvider:
        """Create a TTS provider based on configuration.
        
        Args:
            config: TTS configuration
            
        Returns:
            TTS provider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_map = {
            TTSProvider.ELEVENLABS: ElevenLabsProvider,
            TTSProvider.GOOGLE: GoogleTTSProvider,
            TTSProvider.OPENAI: OpenAITTSProvider,
            TTSProvider.AMAZON: AmazonPollyProvider,
        }
        
        provider_class = provider_map.get(config.provider)
        if not provider_class:
            raise ValueError(f"Unsupported TTS provider: {config.provider}")
        
        try:
            provider = provider_class(config)
            logger.info(f"Created TTS provider: {config.provider.value}")
            return provider
        except Exception as e:
            logger.error(f"Failed to create TTS provider {config.provider.value}: {e}")
            raise
    
    @staticmethod
    def from_env(
        provider_name: str,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        language: str = "en-US",
        model: Optional[str] = None,
    ) -> BaseTTSProvider:
        """Create TTS provider from environment configuration.
        
        Args:
            provider_name: Provider name string
            api_key: API key for the provider
            voice_id: Default voice ID
            language: Default language
            model: Model selection
            
        Returns:
            TTS provider instance
        """
        # Map string to enum
        provider_enum_map = {
            "elevenlabs": TTSProvider.ELEVENLABS,
            "google": TTSProvider.GOOGLE,
            "openai": TTSProvider.OPENAI,
            "amazon": TTSProvider.AMAZON,
            "polly": TTSProvider.AMAZON,  # Alias
            "gcp": TTSProvider.GOOGLE,  # Alias
        }
        
        provider_enum = provider_enum_map.get(provider_name.lower())
        if not provider_enum:
            raise ValueError(f"Unknown TTS provider: {provider_name}")
        
        config = TTSConfig(
            provider=provider_enum,
            api_key=api_key,
            voice_id=voice_id,
            language=language,
            model=model,
        )
        
        return TTSFactory.create_provider(config)