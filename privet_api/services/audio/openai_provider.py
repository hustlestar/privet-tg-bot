"""OpenAI TTS provider implementation."""

import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile

from openai import AsyncOpenAI

from .tts_base import BaseTTSProvider

logger = logging.getLogger(__name__)


class OpenAITTSProvider(BaseTTSProvider):
    """OpenAI Text-to-Speech provider."""
    
    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    MODELS = ["tts-1", "tts-1-hd"]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        language: str = "en",
        model: Optional[str] = None,
    ):
        """Initialize OpenAI TTS provider.
        
        Args:
            api_key: OpenAI API key
            voice_id: Default voice ID
            language: Default language
            model: TTS model to use
        """
        super().__init__(api_key, voice_id, language, model)
        
        # Initialize OpenAI client
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            # Use environment variable
            self.client = AsyncOpenAI()
        
        # Default settings
        self.default_voice = voice_id or "nova"
        self.default_model = model or "tts-1"  # tts-1 is faster, tts-1-hd is higher quality
        self.response_format = "mp3"  # Can be mp3, opus, aac, flac
        self.speed = 1.0
        
        logger.info(f"OpenAI TTS initialized with voice: {self.default_voice}, model: {self.default_model}")
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        intensity: Optional[float] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Synthesize speech using OpenAI TTS with retry logic.
        
        Args:
            text: Text to synthesize
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            emotion: Not directly supported by OpenAI, but we can adjust voice selection
            **kwargs: Additional parameters (model, speed, response_format)
            
        Returns:
            Audio bytes or None if failed
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Select voice based on emotion if not specified
                if not voice and emotion:
                    voice = self._select_voice_for_emotion(emotion)
                
                voice = voice or self.default_voice
                
                # Validate voice
                if voice not in self.VOICES:
                    logger.warning(f"Invalid voice '{voice}', using default")
                    voice = self.default_voice
                
                # Get model (quality vs speed tradeoff)
                model = kwargs.get('model', self.default_model)
                if model not in self.MODELS:
                    model = self.default_model
                
                # Speed adjustment (0.25 to 4.0)
                speed = kwargs.get('speed', self.speed)
                speed = max(0.25, min(4.0, speed))
                
                # Create speech with timeout
                response = await asyncio.wait_for(
                    self.client.audio.speech.create(
                        model=model,
                        voice=voice,
                        input=text,
                        response_format=kwargs.get('response_format', self.response_format),
                        speed=speed,
                    ),
                    timeout=30 + (attempt * 10)  # 30s, 40s, 50s
                )
                
                # Convert response to bytes
                audio_bytes = response.content
                
                logger.info(f"OpenAI TTS: Synthesized {len(text)} chars with voice '{voice}'")
                return audio_bytes
                
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"OpenAI TTS timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"OpenAI TTS timeout after {max_retries} attempts")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1 and "rate" in str(e).lower():
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"OpenAI TTS rate limit on attempt {attempt + 1}: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"OpenAI TTS error: {e}")
                    return None
    
    def _select_voice_for_emotion(self, emotion: str) -> str:
        """Select appropriate voice based on emotion.
        
        OpenAI voices have different characteristics:
        - alloy: Neutral, balanced
        - echo: Male, warm
        - fable: British, storyteller
        - onyx: Deep, authoritative
        - nova: Female, friendly
        - shimmer: Female, warm
        
        Args:
            emotion: Emotion descriptor
            
        Returns:
            Voice name
        """
        emotion_voice_map = {
            "cheerful": "nova",
            "friendly": "nova",
            "warm": "shimmer",
            "calm": "alloy",
            "professional": "onyx",
            "authoritative": "onyx",
            "storytelling": "fable",
            "excited": "nova",
            "sad": "echo",
            "serious": "onyx",
        }
        
        return emotion_voice_map.get(emotion.lower(), self.default_voice)
    
    async def list_voices(self) -> Dict[str, Any]:
        """List available OpenAI TTS voices.
        
        Returns:
            Dictionary of available voices
        """
        voices = [
            {"id": "alloy", "name": "Alloy", "description": "Neutral and balanced"},
            {"id": "echo", "name": "Echo", "description": "Male, warm tone"},
            {"id": "fable", "name": "Fable", "description": "British accent, storyteller"},
            {"id": "onyx", "name": "Onyx", "description": "Deep and authoritative"},
            {"id": "nova", "name": "Nova", "description": "Female, friendly tone"},
            {"id": "shimmer", "name": "Shimmer", "description": "Female, warm tone"},
        ]
        
        models = [
            {"id": "tts-1", "name": "TTS-1", "description": "Optimized for speed"},
            {"id": "tts-1-hd", "name": "TTS-1-HD", "description": "Optimized for quality"},
        ]
        
        return {
            "voices": voices,
            "models": models,
            "formats": ["mp3", "opus", "aac", "flac"],
            "speed_range": {"min": 0.25, "max": 4.0},
        }
    
    def get_supported_languages(self) -> list:
        """Get supported languages.
        
        Returns:
            List of language codes
        """
        # OpenAI TTS supports multiple languages with the same voices
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "nl", "tr", "pl", "sv", "da", "no", "fi", "el", "cs", "ro",
            "hu", "uk", "bg", "hr", "sk", "sl", "lt", "lv", "et", "hi",
            "ar", "he", "th", "id", "ms", "vi", "tl"
        ]
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost for OpenAI TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Estimated cost in USD
        """
        # OpenAI TTS pricing
        # tts-1: $0.015 per 1,000 characters
        # tts-1-hd: $0.030 per 1,000 characters
        char_count = len(text)
        
        if self.default_model == "tts-1-hd":
            return (char_count / 1000) * 0.030
        else:
            return (char_count / 1000) * 0.015