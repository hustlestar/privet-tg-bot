"""Google Cloud Text-to-Speech provider implementation."""

import logging
from typing import Optional, Dict, Any
import json

from .base import BaseTTSProvider, TTSConfig

logger = logging.getLogger(__name__)

# Google Cloud TTS will be imported conditionally
try:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    logger.warning("Google Cloud TTS not installed. Install with: pip install google-cloud-texttospeech")


class GoogleTTSProvider(BaseTTSProvider):
    """Google Cloud Text-to-Speech provider."""
    
    def __init__(self, config: TTSConfig):
        """Initialize Google TTS provider.
        
        Args:
            config: TTS configuration
        """
        super().__init__(config)
        
        if not GOOGLE_TTS_AVAILABLE:
            raise ImportError("Google Cloud TTS library not installed")
        
        # Initialize client
        if config.api_key:
            # API key should be path to service account JSON or JSON string
            if config.api_key.startswith('{'):
                # It's a JSON string
                credentials_info = json.loads(config.api_key)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
            else:
                # It's a file path
                credentials = service_account.Credentials.from_service_account_file(config.api_key)
            self.client = texttospeech.TextToSpeechAsyncClient(credentials=credentials)
        else:
            # Use default credentials (from environment)
            self.client = texttospeech.TextToSpeechAsyncClient()
        
        # Default settings
        self.language_code = config.language or "en-US"
        self.voice_name = config.voice_id or "en-US-Neural2-C"  # Female voice
        self.audio_encoding = texttospeech.AudioEncoding.MP3
        
        logger.info(f"Google TTS initialized with voice: {self.voice_name}")
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Synthesize speech using Google Cloud TTS.
        
        Args:
            text: Text to synthesize
            voice: Voice name (e.g., "en-US-Neural2-A")
            emotion: Emotion style (limited support in Google)
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            # Set up the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Select voice
            voice_name = voice or self.voice_name
            language_code = kwargs.get('language', self.language_code)
            
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=kwargs.get('gender', texttospeech.SsmlVoiceGender.NEUTRAL)
            )
            
            # Configure audio
            speaking_rate = self.config.speed
            pitch = self.config.pitch
            
            # Add emotion through speaking rate and pitch
            if emotion:
                speaking_rate, pitch = self._adjust_for_emotion(emotion, speaking_rate, pitch)
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=self.audio_encoding,
                speaking_rate=speaking_rate,
                pitch=pitch,
                volume_gain_db=kwargs.get('volume_gain', 0.0),
            )
            
            # Perform the text-to-speech request
            response = await self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )
            
            logger.info(f"Google TTS: Synthesized {len(text)} chars")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return None
    
    def _adjust_for_emotion(self, emotion: str, rate: float, pitch: float) -> tuple:
        """Adjust speaking rate and pitch for emotion.
        
        Args:
            emotion: Emotion descriptor
            rate: Base speaking rate
            pitch: Base pitch
            
        Returns:
            Tuple of (adjusted_rate, adjusted_pitch)
        """
        emotion_adjustments = {
            "cheerful": (1.1, 2.0),
            "excited": (1.2, 3.0),
            "calm": (0.9, -1.0),
            "sad": (0.85, -2.0),
            "angry": (1.1, 1.0),
            "professional": (1.0, 0.0),
        }
        
        if emotion.lower() in emotion_adjustments:
            rate_mult, pitch_adj = emotion_adjustments[emotion.lower()]
            return rate * rate_mult, pitch + pitch_adj
        
        return rate, pitch
    
    async def list_voices(self) -> Dict[str, Any]:
        """List available Google TTS voices.
        
        Returns:
            Dictionary of available voices
        """
        try:
            # List available voices
            response = await self.client.list_voices()
            
            voices = []
            for voice in response.voices:
                voices.append({
                    "name": voice.name,
                    "language_codes": voice.language_codes,
                    "gender": voice.ssml_gender.name,
                    "natural": "Neural2" in voice.name or "Wavenet" in voice.name,
                })
            
            return {"voices": voices}
            
        except Exception as e:
            logger.error(f"Error listing Google TTS voices: {e}")
            return {"voices": []}
    
    def get_supported_languages(self) -> list:
        """Get supported languages.
        
        Returns:
            List of language codes
        """
        # Google TTS supports many languages
        return [
            "en-US", "en-GB", "en-AU", "en-IN",
            "es-ES", "es-US", "es-MX",
            "fr-FR", "fr-CA",
            "de-DE", "it-IT", "pt-BR", "pt-PT",
            "ru-RU", "ja-JP", "ko-KR", "zh-CN", "zh-TW",
            "ar-XA", "hi-IN", "nl-NL", "pl-PL", "tr-TR",
            "sv-SE", "da-DK", "no-NO", "fi-FI"
        ]
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost for Google Cloud TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Estimated cost in USD
        """
        # Google Cloud TTS pricing (approximate)
        # Standard voices: $4 per 1 million characters
        # Neural2/WaveNet voices: $16 per 1 million characters
        char_count = len(text)
        
        if "Neural2" in self.voice_name or "Wavenet" in self.voice_name:
            return (char_count / 1_000_000) * 16.00
        else:
            return (char_count / 1_000_000) * 4.00