"""Base TTS provider interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseTTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        language: str = "en",
        model: Optional[str] = None,
    ):
        """Initialize TTS provider.
        
        Args:
            api_key: API key for the service
            voice_id: Default voice ID
            language: Default language
            model: Model to use (provider-specific)
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.language = language
        self.model = model
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        intensity: Optional[float] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice ID override
            emotion: Emotion/tone for synthesis
            intensity: Emotion intensity (0.0-1.0)
            **kwargs: Provider-specific parameters
            
        Returns:
            Audio data as bytes or None if failed
        """
        pass
    
    @abstractmethod
    async def list_voices(self) -> Dict[str, Any]:
        """List available voices.
        
        Returns:
            Dictionary of available voices
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> list:
        """Get list of supported languages.
        
        Returns:
            List of language codes
        """
        pass