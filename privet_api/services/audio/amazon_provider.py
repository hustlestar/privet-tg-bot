"""Amazon Polly TTS provider implementation."""

import logging
from typing import Optional, Dict, Any

from .base import BaseTTSProvider, TTSConfig

logger = logging.getLogger(__name__)

# Amazon Polly will be imported conditionally
try:
    import boto3
    AMAZON_POLLY_AVAILABLE = True
except ImportError:
    AMAZON_POLLY_AVAILABLE = False
    logger.warning("boto3 not installed. Install with: pip install boto3")


class AmazonPollyProvider(BaseTTSProvider):
    """Amazon Polly Text-to-Speech provider."""
    
    def __init__(self, config: TTSConfig):
        """Initialize Amazon Polly provider.
        
        Args:
            config: TTS configuration
        """
        super().__init__(config)
        
        if not AMAZON_POLLY_AVAILABLE:
            raise ImportError("boto3 library not installed")
        
        # Initialize Polly client
        # API key format: "access_key_id,secret_access_key,region"
        if config.api_key:
            parts = config.api_key.split(',')
            if len(parts) >= 2:
                self.client = boto3.client(
                    'polly',
                    aws_access_key_id=parts[0],
                    aws_secret_access_key=parts[1],
                    region_name=parts[2] if len(parts) > 2 else 'us-east-1'
                )
            else:
                # Use default credentials
                self.client = boto3.client('polly')
        else:
            # Use default AWS credentials
            self.client = boto3.client('polly')
        
        # Default settings
        self.default_voice = config.voice_id or "Joanna"  # US English female
        self.default_engine = "neural"  # neural or standard
        self.output_format = "mp3"
        self.language_code = config.language or "en-US"
        
        logger.info(f"Amazon Polly initialized with voice: {self.default_voice}")
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Synthesize speech using Amazon Polly.
        
        Args:
            text: Text to synthesize
            voice: Voice ID (e.g., "Joanna", "Matthew")
            emotion: Emotion style (limited support via SSML)
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            voice_id = voice or self.default_voice
            engine = kwargs.get('engine', self.default_engine)
            
            # Build SSML if emotion is specified
            if emotion:
                text = self._build_ssml_with_emotion(text, emotion)
                text_type = "ssml"
            else:
                text_type = "text"
            
            # Synthesize speech
            response = self.client.synthesize_speech(
                Text=text,
                TextType=text_type,
                OutputFormat=self.output_format,
                VoiceId=voice_id,
                Engine=engine,
                LanguageCode=kwargs.get('language_code', self.language_code),
            )
            
            # Read audio stream
            audio_bytes = response['AudioStream'].read()
            
            logger.info(f"Amazon Polly: Synthesized {len(text)} chars with voice '{voice_id}'")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Amazon Polly error: {e}")
            return None
    
    def _build_ssml_with_emotion(self, text: str, emotion: str) -> str:
        """Build SSML markup with emotion.
        
        Args:
            text: Plain text
            emotion: Emotion descriptor
            
        Returns:
            SSML marked up text
        """
        # Amazon Polly supports limited emotion through prosody
        emotion_prosody = {
            "cheerful": {"rate": "110%", "pitch": "+5%"},
            "excited": {"rate": "120%", "pitch": "+10%"},
            "calm": {"rate": "90%", "pitch": "-5%"},
            "sad": {"rate": "85%", "pitch": "-10%"},
            "angry": {"rate": "110%", "volume": "+5dB"},
            "whisper": {"volume": "-10dB"},
        }
        
        if emotion.lower() in emotion_prosody:
            prosody = emotion_prosody[emotion.lower()]
            prosody_attrs = " ".join([f'{k}="{v}"' for k, v in prosody.items()])
            return f'<speak><prosody {prosody_attrs}>{text}</prosody></speak>'
        
        return f'<speak>{text}</speak>'
    
    async def list_voices(self) -> Dict[str, Any]:
        """List available Amazon Polly voices.
        
        Returns:
            Dictionary of available voices
        """
        try:
            response = self.client.describe_voices()
            
            voices = []
            for voice in response['Voices']:
                voices.append({
                    "id": voice['Id'],
                    "name": voice['Name'],
                    "language_code": voice['LanguageCode'],
                    "language_name": voice['LanguageName'],
                    "gender": voice['Gender'],
                    "neural": 'neural' in voice.get('SupportedEngines', []),
                })
            
            return {"voices": voices}
            
        except Exception as e:
            logger.error(f"Error listing Polly voices: {e}")
            return {"voices": []}
    
    def get_supported_languages(self) -> list:
        """Get supported languages.
        
        Returns:
            List of language codes
        """
        # Amazon Polly supported languages
        return [
            "en-US", "en-GB", "en-AU", "en-IN", "en-NZ", "en-ZA", "en-WLS",
            "es-ES", "es-US", "es-MX",
            "fr-FR", "fr-CA",
            "de-DE", "de-AT",
            "it-IT",
            "pt-BR", "pt-PT",
            "ru-RU",
            "ja-JP",
            "ko-KR",
            "zh-CN",
            "ar", "hi-IN", "nl-NL", "pl-PL", "tr-TR",
            "sv-SE", "da-DK", "no-NO", "is-IS", "ro-RO", "cy-GB"
        ]
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost for Amazon Polly.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Estimated cost in USD
        """
        # Amazon Polly pricing
        # Standard voices: $4 per 1 million characters
        # Neural voices: $16 per 1 million characters
        char_count = len(text)
        
        if self.default_engine == "neural":
            return (char_count / 1_000_000) * 16.00
        else:
            return (char_count / 1_000_000) * 4.00