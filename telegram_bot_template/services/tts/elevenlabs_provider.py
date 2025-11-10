"""ElevenLabs TTS provider implementation."""

import logging
from typing import Optional, Dict, Any
from elevenlabs.client import AsyncElevenLabs

from .base import BaseTTSProvider, TTSConfig

logger = logging.getLogger(__name__)


class ElevenLabsProvider(BaseTTSProvider):
    """ElevenLabs TTS provider."""
    
    def __init__(self, config: TTSConfig):
        """Initialize ElevenLabs provider.
        
        Args:
            config: TTS configuration
        """
        super().__init__(config)
        
        if not config.api_key:
            raise ValueError("ElevenLabs API key is required")
        
        self.client = AsyncElevenLabs(api_key=config.api_key)
        
        # Default settings
        self.default_voice = config.voice_id or "Rachel"
        self.default_model = config.model or "eleven_multilingual_v2"
        
        logger.info(f"ElevenLabs TTS initialized with voice: {self.default_voice}")
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Synthesize speech using ElevenLabs.
        
        Args:
            text: Text to synthesize
            voice: Voice ID or name
            emotion: Emotion style (affects voice settings)
            **kwargs: Additional ElevenLabs parameters
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            voice_id = voice or self.default_voice
            
            # Map emotion to voice settings
            voice_settings = self._get_voice_settings(emotion)
            
            # Override with any provided settings
            if 'voice_settings' in kwargs:
                voice_settings.update(kwargs['voice_settings'])
            
            # Generate audio using the correct ElevenLabs API method
            # The AsyncElevenLabs client uses 'generate' method
            from elevenlabs import Voice
            
            audio_stream = await self.client.generate(
                text=text,
                voice=voice_id,
                model=kwargs.get('model', self.default_model),
            )
            
            # Collect audio chunks
            audio_bytes = b""
            async for chunk in audio_stream:
                audio_bytes += chunk
            
            logger.info(f"ElevenLabs: Synthesized {len(text)} chars, {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            return None
    
    def _get_voice_settings(self, emotion: Optional[str]) -> Dict[str, Any]:
        """Get voice settings based on emotion.
        
        Args:
            emotion: Emotion descriptor
            
        Returns:
            Voice settings dictionary
        """
        base_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        }
        
        # Emotion presets
        emotion_presets = {
            "cheerful": {"stability": 0.4, "style": 0.7},
            "calm": {"stability": 0.8, "style": 0.2},
            "excited": {"stability": 0.3, "style": 0.9},
            "sad": {"stability": 0.7, "style": 0.3},
            "angry": {"stability": 0.3, "style": 0.8},
            "professional": {"stability": 0.9, "style": 0.1},
        }
        
        if emotion and emotion.lower() in emotion_presets:
            base_settings.update(emotion_presets[emotion.lower()])
        
        return base_settings
    
    async def list_voices(self) -> Dict[str, Any]:
        """List available ElevenLabs voices.
        
        Returns:
            Dictionary of available voices
        """
        try:
            voices = await self.client.voices.get_all()
            return {
                "voices": [
                    {
                        "id": voice.voice_id,
                        "name": voice.name,
                        "category": voice.category,
                        "description": voice.description,
                    }
                    for voice in voices.voices
                ]
            }
        except Exception as e:
            logger.error(f"Error listing ElevenLabs voices: {e}")
            return {"voices": []}
    
    def get_supported_languages(self) -> list:
        """Get supported languages.
        
        Returns:
            List of language codes
        """
        # ElevenLabs multilingual model supports many languages
        return [
            "en", "es", "fr", "de", "it", "pt", "pl", "ru",
            "nl", "sv", "ar", "hi", "ja", "ko", "zh", "tr"
        ]
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost for ElevenLabs.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Estimated cost in USD
        """
        # ElevenLabs pricing (approximate)
        # ~$0.30 per 1000 characters for standard voices
        char_count = len(text)
        return (char_count / 1000) * 0.30