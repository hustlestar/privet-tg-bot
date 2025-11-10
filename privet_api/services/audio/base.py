"""Base TTS provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class TTSProvider(Enum):
    """Available TTS providers."""
    ELEVENLABS = "elevenlabs"
    GOOGLE = "google"
    OPENAI = "openai"
    AMAZON = "amazon"
    AZURE = "azure"


@dataclass
class TTSConfig:
    """Configuration for TTS providers."""
    provider: TTSProvider
    api_key: Optional[str] = None
    
    # Provider-specific settings
    voice_id: Optional[str] = None  # For ElevenLabs, OpenAI
    language: str = "en-US"  # For Google, Amazon
    
    # Voice characteristics
    speed: float = 1.0  # Speech speed multiplier
    pitch: float = 0.0  # Pitch adjustment
    
    # Quality settings
    model: Optional[str] = None  # Model selection for providers that support it
    quality: str = "standard"  # standard, premium, etc.
    
    # Additional provider-specific config
    extra_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_config is None:
            self.extra_config = {}


class BaseTTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    def __init__(self, config: TTSConfig):
        """Initialize TTS provider with configuration.
        
        Args:
            config: TTS configuration
        """
        self.config = config
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Optional voice override
            emotion: Optional emotion/style
            **kwargs: Provider-specific parameters
            
        Returns:
            Audio bytes or None if failed
        """
        pass
    
    @abstractmethod
    async def list_voices(self) -> Dict[str, Any]:
        """List available voices for this provider.
        
        Returns:
            Dictionary of available voices with metadata
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> list:
        """Get list of supported languages.
        
        Returns:
            List of language codes
        """
        pass
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost for synthesizing text.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Estimated cost in USD
        """
        # Default implementation based on character count
        # Override in specific providers for accurate pricing
        char_count = len(text)
        return 0.0  # Base implementation returns 0